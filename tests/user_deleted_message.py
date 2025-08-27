from courier import Message


class UserDeletedMessage(Message):
    def __init__(self, user):
        self.user = user
