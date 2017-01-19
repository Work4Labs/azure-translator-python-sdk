"""Azure Translator module."""
import xml.etree.ElementTree as ET

import requests


class Translator(object):
    """
    Translator class, connects to Azure Translator API:

        http://docs.microsofttranslator.com/text-translate.html
    """
    DEFAULT_LANGUAGE = 'en'
    TOKEN_API = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    TRANSLATE_API = 'https://api.microsofttranslator.com/v2/http.svc/Translate'


    def __init__(self, api_key):
        self.api_key = api_key

    @staticmethod
    def _api_error(request_error):
        return AzureApiError(
            unicode(request_error),
            response=request_error.response,
            request=request_error.request
        )

    def get_access_token(self):
        """
        Retrieve an access token in order to use the Translator API.
        """
        resp = requests.post(
            self.TOKEN_API,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/jwt',
                'Ocp-Apim-Subscription-Key': self.api_key,
            }
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise self._api_error(error)
        return resp.content

    def translate(self, text, to=DEFAULT_LANGUAGE, source_language=None):
        """
        Translate some text into some language. Target language default to english.

        :param text:               the text to translate
        :param to:                 the target language
        :param source_language:    optional source language
        """
        params = {
            'text': text,
            'to': to,
        }
        if source_language:
            params['from'] = source_language
        resp = requests.get(
            self.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer {}'.format(self.get_access_token()),
                'Accept': 'application/xml',
            },
            params=params
        )
        try:
            resp.raise_for_status()
        except requests.exceptions.HTTPError as error:
            raise self._api_error(error)

        try:
            return ET.fromstring(resp.content.encode('utf-8')).text
        except ET.ParseError as e:
            raise AzureApiBadFormatError(unicode(e), response=resp, request=getattr(resp, 'request', None))


class AzureApiError(Exception):
    """
    Raised when the API returns a non-200 body.
    """
    def __init__(self, *args, **kwargs):
        self.response = kwargs.pop('response', None)
        self.request = kwargs.pop('request', None)
        super(AzureApiError, self).__init__(*args, **kwargs)


class AzureApiBadFormatError(AzureApiError):
    """
    Raised when the API returns a malformed error.
    """
