from unittest.mock import Mock, patch, MagicMock
import threading
import time
from pika.exceptions import AMQPConnectionError

from easter.rabbitmq import RabbitMQConnectionFactory, RabbitMQConsumer
from easter import Mailbox


class TestMailbox(Mailbox):
    supported_message_types = []

    def handle(self, message):
        pass


def test_consumer_default_parameters():
    factory = RabbitMQConnectionFactory()
    consumer = RabbitMQConsumer(factory, [])

    assert consumer.max_reconnect_attempts == 0
    assert consumer.reconnect_delay == 5.0


def test_consumer_custom_parameters():
    factory = RabbitMQConnectionFactory()
    consumer = RabbitMQConsumer(
        factory, [], max_reconnect_attempts=5, reconnect_delay=2.0
    )

    assert consumer.max_reconnect_attempts == 5
    assert consumer.reconnect_delay == 2.0


def test_consumer_should_stop_flag():
    factory = RabbitMQConnectionFactory()
    consumer = RabbitMQConsumer(factory, [])

    assert consumer._should_stop is False


@patch("easter.rabbitmq.rabbitmq_consumer.QueueCollectionFactory")
def test_consumer_close_sets_should_stop(mock_queue_factory):
    factory = RabbitMQConnectionFactory()
    consumer = RabbitMQConsumer(factory, [])

    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_channel.is_open = False
    mock_connection.is_open = False

    consumer.connection = mock_connection
    consumer.channel = mock_channel

    consumer.close()

    assert consumer._should_stop is True


@patch("easter.rabbitmq.rabbitmq_consumer.QueueCollectionFactory")
def test_cleanup_connection_handles_exceptions(mock_queue_factory):
    factory = RabbitMQConnectionFactory()
    consumer = RabbitMQConsumer(factory, [])

    mock_connection = MagicMock()
    mock_connection.is_open = True
    mock_connection.close.side_effect = Exception("Connection error")

    mock_channel = MagicMock()
    mock_channel.is_open = True
    mock_channel.close.side_effect = Exception("Channel error")

    consumer.connection = mock_connection
    consumer.channel = mock_channel

    # Should not raise an exception
    consumer._cleanup_connection()


@patch("easter.rabbitmq.rabbitmq_consumer.QueueCollectionFactory")
def test_try_reconnect_returns_negative_when_max_attempts_reached(mock_queue_factory):
    factory = RabbitMQConnectionFactory()
    consumer = RabbitMQConsumer(factory, [], max_reconnect_attempts=3, reconnect_delay=0.01)

    consumer.connection = None
    consumer.channel = None

    result = consumer._try_reconnect(reconnect_attempts=3)

    assert result == -1


@patch("easter.rabbitmq.rabbitmq_consumer.QueueCollectionFactory")
def test_try_reconnect_increments_attempts_on_failure(mock_queue_factory):
    factory = MagicMock()
    factory.build.side_effect = AMQPConnectionError("Connection refused")

    consumer = RabbitMQConsumer(factory, [], max_reconnect_attempts=5, reconnect_delay=0.01)
    consumer.connection = None
    consumer.channel = None

    result = consumer._try_reconnect(reconnect_attempts=1)

    assert result == 2


@patch("easter.rabbitmq.rabbitmq_consumer.QueueCollectionFactory")
def test_try_reconnect_resets_attempts_on_success(mock_queue_factory):
    mock_connection = MagicMock()
    mock_channel = MagicMock()
    mock_connection.channel.return_value = mock_channel
    mock_queue_factory.return_value.build.return_value = []

    factory = MagicMock()
    factory.build.return_value = mock_connection

    consumer = RabbitMQConsumer(factory, [], max_reconnect_attempts=5, reconnect_delay=0.01)
    consumer.connection = None
    consumer.channel = None

    result = consumer._try_reconnect(reconnect_attempts=2)

    assert result == 0
