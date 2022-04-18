import requests
from urllib.parse import urlparse
from requests_oauthlib import OAuth2Session
from requests.adapters import HTTPAdapter
from urllib3.util import Retry

from .jwt_auth import JWT_AUTH
from .s2s_auth import S2S_AUTH
from .exceptions import ZoomAPIError, ZoomAPIDatetimeError


class ZoomAPIClient(object):
    def __init__(
        self,
        API_KEY: str = None,  # used for JWT
        API_SECRET: str = None,  # used for JWT
        ACCOUNT_ID: str = None,  # used for S2S oAuth apps
        S2S_CLIENT_ID: str = None,  # used for S2S oAuth apps
        S2S_CLIENT_SECRET: str = None,  # used for S2S oAuth apps
        OAuth2Session: OAuth2Session = None,  # used for standard oAuth app
    ):
        """Zoom API Client

        Specify either API_KEY & API_SECRET to use JWT authentication or oAuth2Session to use oAuth authentication

        Args:
            API_KEY (str, optional): JWT API key from Zoom Marketplace.
            API_SECRET (str, optional): JWT API Secret from Zoom Marketplace.
            OAuth2Session (OAuth2Session, optional): oAuth2 Session to be used by oAuth application

        Raises:
            RuntimeError: If authentication parameters are not passed properly
        """
        self._server = "https://api.zoom.us/v2"

        if (
            (API_KEY == None or API_SECRET == None)
            and (
                ACCOUNT_ID == None or S2S_CLIENT_ID == None or S2S_CLIENT_SECRET == None
            )
            and OAuth2Session == None
        ):
            raise RuntimeError(
                "Must specify either 1) API_KEY and API_SECRET for JWT authentication or 2) OAuth2Session for oAuth authentication"
            )

        elif API_KEY and API_SECRET:
            # using JWT authentication and standard requests session

            s = requests.Session()
            s.auth = JWT_AUTH(API_KEY, API_SECRET)
            s.headers.update({"Content-type": "application/json"})

        elif ACCOUNT_ID and S2S_CLIENT_ID and S2S_CLIENT_SECRET:
            # using S2S oAuth authentication and standard requests session

            s = requests.Session()
            s.auth = S2S_AUTH(ACCOUNT_ID, S2S_CLIENT_ID, S2S_CLIENT_SECRET)
            s.headers.update({"Content-type": "application/json"})

        elif OAuth2Session:
            # using oAuth2 authentication
            s = OAuth2Session

        # Add retry to handle Zoom API server errors and rate limiting
        retry_strategy = Retry(
            total=5,
            status=3,
            backoff_factor=2,
            status_forcelist=[429],
            allowed_methods=["GET", "PUT", "PATCH", "POST", "DELETE"],
        )
        adapter = HTTPAdapter(max_retries=retry_strategy)
        s.mount("https://", adapter)

        s.headers = {"User-Agent": "BasicZoom PythonClient"}

        self._session = s

    def parse_request_response(self, response):
        if response.status_code in [200, 201, 204]:
            if response.content in [b""]:
                return response.status_code
            else:
                try:
                    return response.json()
                except:
                    return response.content

        else:
            if "message" in response.json():
                raise ZoomAPIError(response.json()["message"])
            else:
                raise ZoomAPIError(
                    f"Received status code {response.status_code} on {response.url}"
                )

    def get(
        self,
        endpoint_url: str,
        params: dict = None,
        auto_page: bool = True,
    ):
        """Generic HTTP GET method for Zoom API.

        Note that Zoom API pagination uses next_page_token which other Zoom APIs do not use

        Args:
            endpoint_url (str): endpoint url
            params (dict, optional): parameters used in HTTP query parameters. Defaults to None.
            raw (bool, optional): If set to 'True' will return raw JSON response as returned from Zoom API.  IF set to 'False', this function will complete pagination and return a list of all data returned on key 'key_in_response_to_return'. Defaults to False.

        Raises:
            ValueError: [description]

        Returns:
            [type]: [description]
        """

        if params == None:
            params = {}  # init empty dict

        # If no page size is set, let's increase from the API default of 30
        if "page_size" not in params:
            if endpoint_url in ["/phone/call_logs", "/phone/devices"]:
                # The above APIs allow up to 300 items in page response
                params["page_size"] = "300"
            else:
                # all GET APIS support atleast 100 results, so use this as default value
                params["page_size"] = "100"

        response = self._session.get(f"{self._server}{endpoint_url}", params=params)
        parsed_response = self.parse_request_response(response)

        # If response is a status code (type=int), there is no response body, so we will return status code from API without modification
        if type(parsed_response) == int:
            return parsed_response

        # If key_in_response_to_return is not passed to method, we will return response from API without modification
        if auto_page == False:
            return parsed_response

        # Zoom APIs return a JSON with a key determined by the URL that contains the requested data.
        endpoint_urlparsed = urlparse(endpoint_url)
        key_in_response_to_return = endpoint_urlparsed.path.rsplit("/", 1)[-1]

        # Check for no data in response from API
        if key_in_response_to_return not in parsed_response:
            return parsed_response

        # check for no 'next_page_token'
        if "next_page_token" not in parsed_response:
            return parsed_response

        # check if 'from' and 'to' date was included in parameter.  If so, make sure API is returning this data
        # Some APIs only allow 30 days within a single query, the API response informs about the dates for the results, but
        # If the user is using 'key_in_response_to_return' they won't see this data, so validate API request & response dates match

        date_error = False

        if params.get("from") is not None:
            if params.get("from") != parsed_response.get("from"):
                date_error = True

        if params.get("to") is not None:
            if params.get("to") != parsed_response.get("to"):
                date_error = True

        if date_error:
            # the request specified a from and to date range, but the API response is not the same.  Error here to let user troubleshoot mismatch
            raise ZoomAPIDatetimeError(
                request_from=params.get("from"),
                request_to=params.get("to"),
                response_from=parsed_response.get("from"),
                response_to=parsed_response.get("to"),
            )

        # At this point, we have decided that we will handle paging within this class method.  Page through all data and return a list of all responses
        data_to_return = parsed_response

        while parsed_response["next_page_token"] != "":
            params["next_page_token"] = parsed_response["next_page_token"]

            parsed_response = self.get(endpoint_url, params, auto_page=False)

            if key_in_response_to_return in parsed_response:
                data_to_return[key_in_response_to_return].extend(
                    parsed_response[key_in_response_to_return]
                )

        del data_to_return["next_page_token"]

        return data_to_return

    def post(self, endpoint_url: str, data: dict):
        response = self._session.post(f"{self._server}{endpoint_url}", json=data)
        return self.parse_request_response(response)

    def patch(self, endpoint_url: str, params: dict = None, data: dict = None):
        response = self._session.patch(
            f"{self._server}{endpoint_url}", params=params, json=data
        )
        return self.parse_request_response(response)

    def delete(self, endpoint_url: str):
        response = self._session.delete(f"{self._server}{endpoint_url}")
        return self.parse_request_response(response)
