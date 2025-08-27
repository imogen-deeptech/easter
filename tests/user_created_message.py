from easter import Message


class UserCreatedMessage(Message):
    def __init__(self, user):
        self.user = user
