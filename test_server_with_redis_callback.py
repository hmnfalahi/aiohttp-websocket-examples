from asyncio import wait_for, TimeoutError

import pytest

from redis_ import push_async
from conftest import application_type


class TestWS:
    @classmethod
    def setup_class(cls):
        application_type('redis_callback')

    @staticmethod
    async def test_websocket(websocket_session):
        async with websocket_session() as ws:
            await push_async('queue1', 'Hello World!')
            assert await ws.receive_str() == 'Hello World!'

            await push_async('queue2', 'Hello World!')
            with pytest.raises(TimeoutError):
                await wait_for(ws.receive_str(), timeout=1)

            await ws.send_str('keep')
            assert await ws.receive_str() == 'keep/answer'

            await ws.send_str('close')
            assert await ws.receive_str() == 'closing'

