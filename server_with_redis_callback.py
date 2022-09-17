import asyncio
import logging
import traceback
from concurrent.futures import CancelledError

import aiohttp
from aiohttp import web

from redis_ import flush_all_async, pop_async, async_redis


logging.basicConfig(level=logging.INFO)


async def websocket_handler(request):
    logging.info('New connection!!!')

    ws = web.WebSocketResponse()
    await ws.prepare(request)
    app_state()['connections'].add(ws)

    logging.info('Socket stored')

    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.send_str('closing')
                    break

                await ws.send_str(msg.data+'/answer')

            elif msg.type == aiohttp.WSMsgType.ERROR:
                logging.info(
                    f'WS connection closed with exception {ws.exception()}'
                )

    except CancelledError as exp:
        logging.info(f'WebSocket CancelError:\n{exp}\n{traceback.print_exc()}')

    except Exception as exp:
        logging.error(
            f'WebSocket handler error:\n{exp}\n{traceback.print_exc()}'
        )

    finally:
        app_state()['connections'].remove(ws)
        await ws.close()
        logging.info('WebSocket connection closed')


async def worker(name):
    await flush_all_async()
    while True:
        try:
            message = await pop_async(name)
            if not message:

                await asyncio.sleep(1)
                continue

            ws_connections = app_state()['connections']
            for ws in ws_connections:
                if ws is None or ws.closed:
                    app_state()['connections'].remove(ws)
                    continue
                await ws.send_str(message)

        except Exception as exc:
            logging.critical(exc, exc_info=True)


async def start_workers(app):
    queue_name = 'queue1'
    loop = asyncio.get_event_loop()
    app_state()['queue_name'] = queue_name
    app_state()['connections'] = set()
    app_state()['message_dispatcher'] = loop.create_task(worker(queue_name))


async def cleanup_background_tasks(app):
    pass


async def prepare_session_manager(app):
    await async_redis()


def app_state():
    return app['state']


app = web.Application()
app.add_routes([web.get('/', websocket_handler)])
app['state'] = {}
app.on_startup.append(prepare_session_manager)
app.on_startup.append(start_workers)
app.on_cleanup.append(cleanup_background_tasks)

