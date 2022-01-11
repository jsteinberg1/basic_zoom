class baseError(Exception):
    def __str__(self):
        return self.message


class ZoomAPIError(baseError):
    """Base class for exceptions in this module."""

    def __init__(self, *args):
        if args:
            self.message = args[0]
        else:
            self.message = None


class ZoomAPIDatetimeError(baseError):
    """Base class for exceptions in this module."""

    def __init__(
        self,
        request_from: str = None,
        request_to: str = None,
        response_from: str = None,
        response_to: str = None,
    ):
        self.request_from = request_from
        self.request_to = request_to
        self.response_from = response_from
        self.response_to = response_to
        self.message = ""

        if request_from and request_to and response_from and response_to:
            self.message = f"Request include date from:{request_from} to:{request_to} but response included from:{response_from} to:{response_to}. This may be due to API date range limitations."

        elif request_from and response_from:
            self.message = f"Request include date from:{request_from} but response included from:{response_from}. This may be due to API date range limitations."

        elif request_to and response_to:
            self.message = f"Request include date to:{request_to} but response included to:{response_to}. This may be due to API date range limitations."

        else:
            self.message = f"Unknown date errir from:{request_from} to:{request_to} but response included from:{response_from} to:{response_to}. This may be due to API date range limitations."
