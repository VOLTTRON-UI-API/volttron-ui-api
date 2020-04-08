import uuid

class TokenHandler(object):
    def __init__(self):
        self.active_tokens = {}

    def generate_token(self, username, password):
        key = (username, password)
        auth_token = str(uuid.uuid4())

        self.active_tokens[key] = auth_token
        return auth_token

    def retrieve_token(self, username, password):
        key = (username, password)
        
        try:
            return self.active_tokens[key]
        except:
            return None

    def validate_token(self, token):
        return token in self.active_tokens.values()

    def remove_token(self, username, password):
        key = (username, password)
        try:
            self.active_tokens.pop(key)
            return True
        except KeyError:
            return False
