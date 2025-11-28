import threading
import time
from typing import List
from easter.mailbox import Mailbox
from easter.message import Message
from easter.consumer import Consumer
from easter.rabbitmq.factories.queue_collection_factory import QueueCollectionFactory
from easter.rabbitmq.rabbitmq_connection_factory import RabbitMQConnectionFactory


class RabbitMQConsumer(Consumer):
    def __init__(
        self,
        connection_factory: RabbitMQConnectionFactory,
        mailboxes: List[Mailbox],
        max_reconnect_attempts: int = 0,
        reconnect_delay: float = 5.0,
    ):
        self.connection_factory = connection_factory
        self.mailboxes = mailboxes
        self.max_reconnect_attempts = max_reconnect_attempts
        self.reconnect_delay = reconnect_delay
        self.consumer_thread = None
        self.connection = None
        self.channel = None
        self._should_stop = False

    def consume(self):
        self._should_stop = False
        self._setup_connection()
        self.consumer_thread = threading.Thread(target=self._consuming_loop)
        self.consumer_thread.start()

    def _setup_connection(self):
        queue_factory = QueueCollectionFactory()
        self.connection = self.connection_factory.build()
        self.channel = self.connection.channel()

        for queue, mailbox in queue_factory.build(self.channel, self.mailboxes):
            message_handler = self.get_message_handler(mailbox)
            self.channel.basic_consume(queue=queue, on_message_callback=message_handler)

    def close(self):
        self._should_stop = True
        try:
            if self.channel and self.channel.is_open:
                self.channel.stop_consuming()
                self.channel.close()

            if self.connection and self.connection.is_open:
                self.connection.close()

            if self.consumer_thread and self.consumer_thread.is_alive():
                self.consumer_thread.join()
        except Exception:
            pass

    def _consuming_loop(self):
        reconnect_attempts = 0
        while not self._should_stop:
            try:
                if self.channel is not None and self.channel.is_open:
                    self.channel.start_consuming()
            except Exception:
                if self._should_stop:
                    break
                reconnect_attempts = self._try_reconnect(reconnect_attempts)
                if reconnect_attempts < 0:
                    break

    def _try_reconnect(self, reconnect_attempts: int) -> int:
        if self.max_reconnect_attempts > 0 and reconnect_attempts >= self.max_reconnect_attempts:
            return -1

        self._cleanup_connection()
        time.sleep(self.reconnect_delay)

        try:
            self._setup_connection()
            return 0
        except Exception:
            return reconnect_attempts + 1

    def _cleanup_connection(self):
        try:
            if self.channel and self.channel.is_open:
                self.channel.close()
        except Exception:
            pass

        try:
            if self.connection and self.connection.is_open:
                self.connection.close()
        except Exception:
            pass

    def get_message_handler(self, mailbox):
        def message_handler(channel, method, properties, body):
            try:
                serialized_message = body.decode("utf-8")
                message = Message.deserialize(serialized_message)

                if type(message) in mailbox.supported_message_types:
                    mailbox.handle(message)

                channel.basic_ack(delivery_tag=method.delivery_tag)
            except Exception as exception:
                print("Error processing message:", exception)
                channel.basic_nack(delivery_tag=method.delivery_tag)

        return message_handler
