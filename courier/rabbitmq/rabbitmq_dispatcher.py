from courier.message import Message
from courier.dispatcher import Dispatcher
from courier.rabbitmq.rabbitmq_connection_factory import RabbitMQConnectionFactory


class RabbitMQDispatcher(Dispatcher):
    def __init__(self, connection_factory: RabbitMQConnectionFactory):
        self.connection_factory = connection_factory

    def dispatch(self, message: Message):
        with self.connection_factory.build() as connection:
            channel = connection.channel()

            serialized_message = message.serialize()
            channel.basic_publish(
                routing_key="#",
                exchange=message.message_type,
                body=serialized_message.encode("utf-8"),
            )
