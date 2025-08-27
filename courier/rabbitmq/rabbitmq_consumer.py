from typing import List
from courier.mailbox import Mailbox
from courier.consumer import Consumer
from courier.delivery import Delivery
from courier.rabbitmq.factories.queue_collection_factory import QueueCollectionFactory
from courier.rabbitmq.rabbitmq_connection_factory import RabbitMQConnectionFactory


class RabbitMQConsumer(Consumer):
    def __init__(
        self, connection_factory: RabbitMQConnectionFactory, mailboxes: List[Mailbox]
    ):
        self.connection_factory = connection_factory
        self.mailboxes = mailboxes

    def consume(self):
        queue_collection_factory = QueueCollectionFactory()
        connection = self.connection_factory.build()
        channel = connection.channel()

        for queue_name, mailbox in queue_collection_factory.build(
            channel, self.mailboxes
        ):
            message_handler = self.get_message_handler(mailbox)
            channel.basic_consume(queue=queue_name, on_message_callback=message_handler)
        channel.start_consuming()

    def close(self):
        pass

    def get_message_handler(self, mailbox):
        def message_handler(ch, method, properties, body):
            message = body.decode("utf-8")
            delivery = Delivery.from_serialized_message(message)

            if delivery.message_type in mailbox.supported_message_types:
                mailbox.handle(delivery)

        return message_handler
