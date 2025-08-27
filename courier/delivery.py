import json


class Delivery(object):
    def __init__(self, message_type, message_content):
        self.message_type = message_type
        self.message_content = message_content

    @staticmethod
    def from_serialized_message(serialized_message: str):
        message_dict = json.loads(serialized_message)
        message_type = message_dict["type"]
        message_content = message_dict["content"]

        return Delivery(message_type, message_content)
