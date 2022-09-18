import pika
from pika import PlainCredentials

from awe.helpers import logger


class WebsocketClient:

    def __init__(self):

        self.host = 'localhost'
        self.username = 'guest'
        self.password = 'guest'
        self.exchange_type = 'fanout'
        self.exchange_name = 'ws_exchange'
        self._create_connection()

    def _create_connection(self):
        # The heartbeat timeout value defines after what period of time
        # the peer TCP connection should be considered unreachable (down) by
        # RabbitMQ and client libraries. This value is negotiated between
        # the client and RabbitMQ server at the time of connection.
        # The client must be configured to request heartbeats.
        # A zero value indicates that a peer suggests disabling heartbeats
        # entirely. To disable heartbeats, both peers have to opt in and
        # use the value of 0
        parameters = pika.ConnectionParameters(
            host=self.host,
            heartbeat=0,
            credentials=PlainCredentials(self.username, self.password)
        )
        self.connection = pika.BlockingConnection(parameters=parameters)
        self.channel = self.connection.channel()

        # the exchange parameter is a name of exchange
        # the exchange_type parameter is a type of exchange
        self.channel.exchange_declare(
            exchange=self.exchange_name,
            exchange_type=self.exchange_type,
        )

    def _sender(self, message: str) -> None:

        self.channel.basic_publish(
            exchange=self.exchange_name,
            routing_key='',
            body=message.encode(),
        )

    def sender(self, message: str) -> None:
        try:

            try:
                self._sender(message)

            except Exception as exc:
                logger.error(exc, exc_info=True)
                self._create_connection()
                self._sender(message)

        except Exception as exc:
            logger.error(exc, exc_info=True)

