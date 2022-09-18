import aio_pika
from aio_pika import ExchangeType

from conftest import application_type
from awe.rmq_ import WebsocketClient


class TestWS:
    @classmethod
    def setup_class(cls):
        application_type('rmq_callback')

    @staticmethod
    async def test_websocket(websocket_session):
        connection = await aio_pika.connect(
            host='localhost',
            port=5672,
            login='guest',
            password='guest',
        )

        async with connection:
            channel = await connection.channel()
            exchange = await channel.declare_exchange(
                'ws_exchange',
                ExchangeType.FANOUT,
            )
            queue = await channel.declare_queue(exclusive=True)
            await queue.bind(exchange)

        queue_websocket = WebsocketClient()

        async with websocket_session() as ws:
            queue_websocket.sender('Hello World!')
            assert await ws.receive_str() == 'Hello World!'

            await ws.send_str('keep')
            assert await ws.receive_str() == 'keep/answer'

            await ws.send_str('close')
            assert await ws.receive_str() == 'closing'

