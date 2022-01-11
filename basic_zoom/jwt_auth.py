import requests
import jwt
import datetime


class JWT_AUTH(requests.auth.AuthBase):
    def __init__(
        self,
        API_KEY: str = None,
        API_SECRET: str = None,
    ):

        self._API_KEY = API_KEY
        self._API_SECRET = API_SECRET
        self._jwt = self.generate_new_jwt()

    def generate_new_jwt(self):

        return jwt.encode(
            {
                "iss": self._API_KEY,
                "exp": datetime.datetime.utcnow() + datetime.timedelta(minutes=60),
            },
            self._API_SECRET,
            algorithm="HS256",
            headers={"alg": "HS256", "typ": "JWT"},
        )

    def __call__(self, r):
        # This is called by requests auth

        try:
            jwt.decode(self._jwt, self._API_SECRET, algorithms=["HS256"])

        except jwt.ExpiredSignatureError:
            # JWT has expired, generate new token
            self._jwt = self.generate_new_jwt()

        finally:
            # jwt_auth_header = self._jwt.decode("utf-8")
            jwt_auth_header = self._jwt
            r.headers["Authorization"] = f"Bearer {jwt_auth_header}"
            return r
