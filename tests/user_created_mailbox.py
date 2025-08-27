from courier import Mailbox
from tests.user_created_message import UserCreatedMessage


class UserCreatedMailbox(Mailbox):
    last_message = None
    received_messages = 0
    supported_message_types = [UserCreatedMessage]

    def handle(self, message):
        self.last_message = message
        self.received_messages += 1
