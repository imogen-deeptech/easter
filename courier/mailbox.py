from abc import ABC, abstractmethod
from courier.message import Message


class Mailbox(ABC):
    supported_message_types = []

    @abstractmethod
    def handle(self, message: Message):
        pass
