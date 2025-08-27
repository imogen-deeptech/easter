import pika
from typing import List
from courier.mailbox import Mailbox
from courier.rabbitmq.factories.queue_exchange_factory import QueueExchangeFactory
from courier.rabbitmq.factories.queue_factory import QueueFactory


class QueueCollectionFactory(object):
    def build(self, channel: pika.channel.Channel, mailboxes: List[Mailbox]):
        queue_factory = QueueFactory()
        exchange_factory = QueueExchangeFactory()
        queues = []

        for mailbox in mailboxes:
            queue_name = queue_factory.build(channel, mailbox)

            for message_type in mailbox.supported_message_types:
                exchange_factory.build(channel, queue_name, message_type)

            queues.append((queue_name, mailbox))

        return queues
