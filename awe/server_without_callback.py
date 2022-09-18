import traceback
from concurrent.futures import CancelledError

import aiohttp
from aiohttp import web

from awe.helpers import logger


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


async def start_workers(app):
    app_state()['connections'] = set()


async def cleanup_background_connections(app):
    for ws_connection in app_state()['connections']:
        await ws_connection.close()


def app_state():
    return app['state']


app = web.Application()
app.add_routes([web.get('/', websocket_handler)])
app['state'] = {}
app.on_startup.append(start_workers)
app.on_cleanup.append(cleanup_background_connections)

