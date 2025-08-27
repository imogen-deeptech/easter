from abc import ABC, abstractmethod
from courier.delivery import Delivery


class Mailbox(ABC):
    supported_message_types = []

    @abstractmethod
    def handle(self, delivery: Delivery):
        pass
