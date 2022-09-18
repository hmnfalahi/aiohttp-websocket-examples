import asyncio
import traceback
from concurrent.futures import CancelledError

import aio_pika
import aiohttp
from aio_pika import ExchangeType
from aiohttp import web

from helpers import logger


async def websocket_handler(request):
    logger.info('New connection!!!')

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app_state()['connections'].add(ws)

    logger.info('Socket stored')

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.send_str('closing')
                    break

                await ws.send_str(msg.data+'/answer')

            elif msg.type == aiohttp.WSMsgType.ERROR:
                logger.info(
                    f'WS connection closed with exception {ws.exception()}'
                )

    except CancelledError as exp:
        logger.info(f'WebSocket CancelError:\n{exp}\n{traceback.print_exc()}')

    except Exception as exp:
        logger.error(
            f'WebSocket handler error:\n{exp}\n{traceback.print_exc()}'
        )

    finally:
        app_state()['connections'].remove(ws)
        await ws.close()
        logger.info('WebSocket connection closed')


async def callback():
    try:
        async with await _create_rabbitmq_connection() as connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                'ws_exchange',
                ExchangeType.FANOUT,
            )
            queue = await channel.declare_queue(exclusive=True)
            await queue.bind(exchange)
            async with queue.iterator() as queue_iter:
                async for message in queue_iter:
                    async with message.process():
                        ws_connections = app_state()['connections']
                        for ws in ws_connections:
                            if ws is None or ws.closed:
                                app_state()['connections'].remove(ws)
                                continue
                            await ws.send_str(str(message.body.decode()))
    except Exception as exp:
        logger.critical(exp, exc_info=True)


async def _create_rabbitmq_connection():
    return await aio_pika.connect_robust(
        host='localhost',
        port=5672,
        login='guest',
        password='guest',
        reconnect_interval=5,
    )


async def start_workers(app):
    loop = asyncio.get_event_loop()
    app_state()['connections'] = set()
    app_state()['message_dispatcher'] = loop.create_task(callback())


async def cleanup_background_connections(app):
    for session, session_connection in app_state()['connections']:
        await session_connection.close()


def app_state():
    return app['state']


app = web.Application()
app.add_routes([web.get('/', websocket_handler)])
app['state'] = {}
app.on_startup.append(start_workers)
app.on_cleanup.append(cleanup_background_connections)

