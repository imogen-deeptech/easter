from abc import ABC, abstractmethod
from courier.message import Message


class Dispatcher(ABC):
    @abstractmethod
    def dispatch(self, message: Message):
        pass
