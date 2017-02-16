"""Azure errors module."""
import xml.etree.ElementTree as ET


class BaseAzureException(Exception):
    """
    Base exception for the SDK.
    """
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        self.request = kwargs.pop('request', None)
        super(BaseAzureException, self).__init__(*args, **kwargs)


class AzureApiError(BaseAzureException):
    """
    Raised when the API returns a non-200 body.
    """
    MSG_SEPARATOR = "; "

    def __init__(self, msg, *args, **kwargs):
        response = kwargs.get('response')
        if response is not None:
            try:
                msg = "HTTP status: {}; {}".format(
                    response.status_code,
                    self.MSG_SEPARATOR.join(ET.fromstring(response.content).itertext())
                ).replace('\r\n', self.MSG_SEPARATOR)  # no line breaks
            except ET.ParseError:
                pass

        super(AzureApiError, self).__init__(msg, *args, **kwargs)


class AzureApiBadFormatError(BaseAzureException):
    """
    Raised when the API returns a malformed error.
    """


class AzureCannotGetTokenError(AzureApiError):
    """
    Raised when the API refuses to return a token.
    """

class AzureApiTimeoutError(BaseAzureException):
    """
    Raised when the API times out.
    """
