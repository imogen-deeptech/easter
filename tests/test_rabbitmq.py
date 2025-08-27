import threading
from courier import RabbitMQConnectionFactory, RabbitMQDispatcher, RabbitMQConsumer
from tests.user import User
from tests.user_created_mailbox import UserCreatedMailbox
from tests.user_created_message import UserCreatedMessage

connection_factory = (
    RabbitMQConnectionFactory()
    .with_host("localhost")
    .with_port(5672)
    .with_credentials("rabbit", "32132111")
)

user_created_mailbox = UserCreatedMailbox()
dispatcher = RabbitMQDispatcher(connection_factory)
consumer = RabbitMQConsumer(connection_factory, [user_created_mailbox])


def test_rabbitmq():
    consumer_thread = threading.Thread(target=consumer.consume)
    consumer_thread.start()

    user = User("test_user", "test@example.com")
    message = UserCreatedMessage(user)
    dispatcher.dispatch(message)

    consumer_thread.join(1)
    consumer.close()

    assert (
        user_created_mailbox.last_delivery.message_type
        in user_created_mailbox.supported_message_types
    )

    assert (
        user_created_mailbox.last_delivery.message_content["user"]["name"] == user.name
    )
    assert (
        user_created_mailbox.last_delivery.message_content["user"]["email"]
        == user.email
    )
