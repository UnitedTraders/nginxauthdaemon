class Authenticator(object):
    """Generic authenticator"""
    def __init__(self, config):
        pass

    def authenticate(self, username, password):
        """Main method to authenticate user by password"""
        return False


class DummyAuthenticator(Authenticator):
    def authenticate(self, username, password):
        return username == password
