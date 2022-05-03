import requests
import datetime


class S2S_AUTH(requests.auth.AuthBase):
    def __init__(
        self,
        ACCOUNT_ID: str = None,
        S2S_CLIENT_ID: str = None,
        S2S_CLIENT_SECRET: str = None,
    ):

        self._ACCOUNT_ID = ACCOUNT_ID
        self._S2S_CLIENT_ID = S2S_CLIENT_ID
        self._S2S_CLIENT_SECRET = S2S_CLIENT_SECRET
        self._S2S_TOKEN_INDEX = "0"
        self._S2S_ACCESS_TOKEN_EXPIRATION = datetime.datetime.utcnow()
        self._S2S_ACCESS_TOKEN = None

    def generate_new_s2s_access_token(self):

        zoom_server_response = requests.post(
            url="https://zoom.us/oauth/token?grant_type=account_credentials"
            + f"&token_index={self._S2S_TOKEN_INDEX}"
            + f"&account_id={self._ACCOUNT_ID}",
            auth=(self._S2S_CLIENT_ID, self._S2S_CLIENT_SECRET),
        )

        zoom_server_response = zoom_server_response.json()
        zoom_access_token = zoom_server_response["access_token"]
        zoom_token_expiration = zoom_server_response["expires_in"]
        zoom_token_scope = zoom_server_response["scope"]

        self._S2S_ACCESS_TOKEN_EXPIRATION = (
            datetime.datetime.utcnow()
            + datetime.timedelta(seconds=zoom_token_expiration - 300)
        )

        return zoom_access_token

    def __call__(self, r):
        # This is called by requests auth

        if (
            datetime.datetime.utcnow() >= self._S2S_ACCESS_TOKEN_EXPIRATION
            or self._S2S_ACCESS_TOKEN == None
        ):
            # token doesnt exist yet or has expired, so renew it....
            self._S2S_ACCESS_TOKEN = self.generate_new_s2s_access_token()

        r.headers["Authorization"] = f"Bearer {self._S2S_ACCESS_TOKEN}"
        return r
