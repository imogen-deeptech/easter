import json
from abc import ABC


class Message(ABC):
    def serialize(self):
        message_content = self.get_content()
        message_as_serialized_json = json.dumps(
            {"type": self.message_type, "content": message_content}
        )

        return message_as_serialized_json

    def get_content(self) -> dict:
        return {}

    @property
    def message_type(self) -> str:
        return self.__class__.__name__
