from contextlib import asynccontextmanager

import pytest
import aiohttp
from aiohttp.web_runner import AppRunner, TCPSite

from awe.server_with_redis_callback import app as redis_websocket_application
from awe.server_without_callback import app as \
    no_callback_websocket_application
from awe.server_with_rmq_callback import app as rmq_websocket_application


type_ = None


def application_type(new_type=None):
    global type_
    if new_type:
        type_ = new_type
    return type_


applications = dict(
    no_callback=no_callback_websocket_application,
    redis_callback=redis_websocket_application,
    rmq_callback=rmq_websocket_application,
)


@pytest.fixture
async def websocket_server(event_loop):
    host = '0.0.0.0'
    application = applications.get(application_type())
    runner = AppRunner(application)
    await runner.setup()
    tcpsite = TCPSite(runner, host, shutdown_timeout=2)
    await tcpsite.start()

    yield tcpsite.name

    await runner.shutdown()
    await runner.cleanup()


@pytest.fixture
async def websocket_session(websocket_server):

    @asynccontextmanager
    async def connect():

        async with aiohttp.ClientSession() as session, \
                session.ws_connect(websocket_server) as ws:
            yield ws

    yield connect

