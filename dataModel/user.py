class User:
    def __init__(self, user_information, session):
        self.session = session
        for k, v in user_information["player"].items():
            setattr(self, k, v)
