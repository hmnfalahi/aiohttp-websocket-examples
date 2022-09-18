from aiohttp import web

from awe.server_with_redis_callback import app as redis_websocket_application
from awe.server_without_callback import app as \
    no_callback_websocket_application
from awe.server_with_rmq_callback import app as rmq_websocket_application


web.run_app(rmq_websocket_application)

