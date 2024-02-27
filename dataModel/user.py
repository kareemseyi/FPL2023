
class User:
    def __init__(self, user_information, session):
        self.session = session
        print(user_information['player'])
        for k, v in user_information['player'].items():
            setattr(self, k, v)
