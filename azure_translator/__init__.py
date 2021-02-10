"""Azure Translator module."""
import json
import requests

from .errors import (
    AzureApiError, AzureApiBadFormatError,
    AzureCannotGetTokenError, AzureApiTimeoutError
)


class Translator(object):
    """
    Translator class, connects to Azure Translator API:

        http://docs.microsofttranslator.com/text-translate.html
    """
    DEFAULT_LANGUAGE = 'en'
    TOKEN_API = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    TRANSLATE_API = 'https://api.cognitive.microsofttranslator.com/translate?api-version=3.0'
    HTTP_TIMEOUT = 10  # seconds


    def __init__(self, api_key):
        self.api_key = api_key

    def get_access_token(self):
        """
        Retrieve an access token in order to use the Translator API.
        """
        try:
            resp = requests.post(
                self.TOKEN_API,
                headers={
                    'Content-Type': 'application/json',
                    'Accept': 'application/jwt',
                    'Ocp-Apim-Subscription-Key': self.api_key,
                },
                timeout=self.HTTP_TIMEOUT
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout as error:
            raise AzureApiTimeoutError(str(error), request=error.request)
        except requests.exceptions.HTTPError as error:
            raise AzureCannotGetTokenError(
                str(error),
                response=error.response,
                request=error.request
            )
        return resp.content

    def translate(self, text, to=DEFAULT_LANGUAGE, source_language=None):
        """
        Translate some text into some language. Target language default to english.

        :param text:               the text to translate
        :param to:                 the target language
        :param source_language:    optional source language
        """
        params = {
            'to': to
        }

        body = [{
            'text' : text
        }]
        if source_language:
            params['from'] = source_language
        try:
            resp = requests.post(
                self.TRANSLATE_API,
                headers={
                    'Authorization': 'Bearer {}'.format(self.get_access_token()),
                    'Content-type': 'application/json',
                    'Accept' : 'application/json'
                },
                params=params,
                json=body,
                timeout=self.HTTP_TIMEOUT
            )
            resp.raise_for_status()
        except requests.exceptions.Timeout as error:
            raise AzureApiTimeoutError(str(error), request=error.request)
        except requests.exceptions.HTTPError as error:
            raise AzureApiError(
                str(error),
                response=error.response,
                request=error.request
            )
        try:
            return resp.json()[0]['translations'][0]['text']
        except (ValueError, KeyError, TypeError) as e:
            raise AzureApiBadFormatError(str(e), response=resp, request=getattr(resp, 'request', None))
