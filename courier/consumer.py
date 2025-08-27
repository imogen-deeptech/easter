from abc import ABC, abstractmethod


class Consumer(ABC):
    @abstractmethod
    def consume(self):
        pass

    @abstractmethod
    def close(self):
        pass
