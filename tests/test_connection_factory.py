from easter.rabbitmq import RabbitMQConnectionFactory


def test_default_heartbeat():
    factory = RabbitMQConnectionFactory()
    assert factory.heartbeat == 60


def test_default_blocked_connection_timeout():
    factory = RabbitMQConnectionFactory()
    assert factory.blocked_connection_timeout == 300


def test_with_heartbeat():
    factory = RabbitMQConnectionFactory().with_heartbeat(30)
    assert factory.heartbeat == 30


def test_with_blocked_connection_timeout():
    factory = RabbitMQConnectionFactory().with_blocked_connection_timeout(120)
    assert factory.blocked_connection_timeout == 120


def test_fluent_interface():
    factory = (
        RabbitMQConnectionFactory()
        .with_host("rabbitmq.example.com")
        .with_port(5673)
        .with_credentials("user", "pass")
        .with_virtual_host("/test")
        .with_heartbeat(45)
        .with_blocked_connection_timeout(180)
    )

    assert factory.host == "rabbitmq.example.com"
    assert factory.port == 5673
    assert factory.username == "user"
    assert factory.password == "pass"
    assert factory.virtual_host == "/test"
    assert factory.heartbeat == 45
    assert factory.blocked_connection_timeout == 180
