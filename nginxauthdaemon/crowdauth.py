import crowd
from auth import Authenticator


class CrowdAuthenticator(Authenticator):
    """Atlassian Crowd authenticator. Requires configuration options CROWD_URL, CROWD_APP_NAME, CROWD_APP_PASSWORD"""
    def __init__(self, config):
        super(CrowdAuthenticator, self).__init__(config)

        app_url = config['CROWD_URL']
        app_user = config['CROWD_APP_NAME']
        app_pass = config['CROWD_APP_PASSWORD']

        self._cs = crowd.CrowdServer(app_url, app_user, app_pass)

    def authenticate(self, username, password):
        result = self._cs.auth_user(username, password)
        return result.get('name') == username
