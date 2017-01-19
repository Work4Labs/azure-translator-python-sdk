"""Azure Translator module."""
import xml.etree.ElementTree as ET

import requests


class Translator(object):
    """
    Translator class, connects to Azure Translator API:

        http://docs.microsofttranslator.com/text-translate.html
    """
    DEFAULT_LANG = 'en'
    TOKEN_API = 'https://api.cognitive.microsoft.com/sts/v1.0/issueToken'
    TRANSLATE_API = 'https://api.microsofttranslator.com/v2/http.svc/Translate'


    def __init__(self, api_key):
        self.api_key = api_key

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
        resp.raise_for_status()
        return resp.content

    def translate(self, text, to=DEFAULT_LANG):
        """
        Translate some text into some language. Target language default to english.

        :param text:               the text to translate
        :param to:                 the target language
        """
        resp = requests.get(
            self.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer {}'.format(self.get_access_token()),
                'Accept': 'application/xml',
            },
            params={
                'text': text,
                'to': to,
            }
        )
        resp.raise_for_status()
        return ET.fromstring(resp.content).text
