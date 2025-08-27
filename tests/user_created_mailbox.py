from courier import Mailbox


class UserCreatedMailbox(Mailbox):
    last_delivery = None
    supported_message_types = ["UserCreatedMessage"]

    def handle(self, delivery):
        self.last_delivery = delivery
