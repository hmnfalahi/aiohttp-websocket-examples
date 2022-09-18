from conftest import application_type


class TestWS:

    @classmethod
    def setup_class(cls):
        application_type('no_callback')

    @staticmethod
    async def test_websocket(websocket_session):
        async with websocket_session() as ws:

            await ws.send_str('Hello World!')
            assert await ws.receive_str() == 'Hello World!/answer'

            await ws.send_str('close')
            assert await ws.receive_str() == 'closing'

