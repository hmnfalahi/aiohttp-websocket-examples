from contextlib import asynccontextmanager

import pytest
import aiohttp
from aiohttp.web_runner import AppRunner, TCPSite

from server_without_callback import app as websocket_application


@pytest.fixture
async def websocket_server(event_loop):
    host = '0.0.0.0'
    runner = AppRunner(websocket_application)
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

