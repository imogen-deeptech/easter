from courier import Message


class UserCreatedMessage(Message):
    def __init__(self, user):
        self.user = user

    def get_content(self):
        return {"user": self.user.__dict__}
