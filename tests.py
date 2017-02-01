# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from mock import patch, MagicMock
from requests.exceptions import HTTPError
from requests.models import Response

from azure_translator import Translator, errors


class TranslatorTestCase(unittest.TestCase):

    translator = Translator('some-api-key')

    def test_init(self):
        self.assertEqual(self.translator.api_key, 'some-api-key')

    @patch('requests.post')
    def test_get_access_token(self, request_post):
        resp = request_post.return_value
        token = self.translator.get_access_token()
        self.assertEqual(token, resp.content)
        request_post.assert_called_with(
            self.translator.TOKEN_API,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/jwt',
                'Ocp-Apim-Subscription-Key': 'some-api-key',
            }
        )
        resp.raise_for_status.assert_called_with()

    @patch('requests.post')
    def test_get_access_token_error(self, request_post):
        resp = request_post.return_value
        resp.raise_for_status.side_effect = HTTPError(
            'boom', response=MagicMock(content="<xml>OUPS</xml>"), request='req'
        )
        with self.assertRaises(errors.AzureCannotGetTokenError):
            self.translator.get_access_token()
        request_post.assert_called_with(
            self.translator.TOKEN_API,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/jwt',
                'Ocp-Apim-Subscription-Key': 'some-api-key',
            }
        )
        resp.raise_for_status.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value='super-token')
    @patch('requests.get', return_value=MagicMock(
        content='<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">I am tired</string>'
    ))
    def test_translate(self, request_get, get_access_token):
        self.assertEqual(self.translator.translate(text='Je suis fatigué'), 'I am tired')
        request_get.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/xml',
            },
            params={
                'text': 'Je suis fatigué',
                'to': self.translator.DEFAULT_LANGUAGE,
            }
        )
        request_get.return_value.raise_for_status.assert_called_with()
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value='super-token')
    @patch('requests.get', return_value=MagicMock(
        content='<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">Je suis</string>'
    ))
    def test_translate_custom_language(self, request_get, get_access_token):
        self.assertEqual(self.translator.translate(text='I am', to='fr'), 'Je suis')
        request_get.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/xml',
            },
            params={
                'text': 'I am',
                'to': 'fr',
            }
        )
        request_get.return_value.raise_for_status.assert_called_with()
        get_access_token.assert_called_with()


    @patch.object(Translator, 'get_access_token', return_value='super-token')
    @patch('requests.get', return_value=MagicMock(
        content='<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">fatigué</string>'.encode('utf-8')
    ))
    def test_translate_response_encoding(self, request_get, get_access_token):
        self.assertEqual(self.translator.translate(text='tired', to='fr'), 'fatigué')
        request_get.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/xml',
            },
            params={
                'text': 'tired',
                'to': 'fr',
            }
        )
        request_get.return_value.raise_for_status.assert_called_with()
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value='super-token')
    @patch('requests.get', return_value=MagicMock(
        content='<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">I am tired</string>'
    ))
    def test_translate_source_lang(self, request_get, get_access_token):
        self.assertEqual(self.translator.translate(text='Je suis fatigué', source_language='fr'), 'I am tired')
        request_get.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/xml',
            },
            params={
                'text': 'Je suis fatigué',
                'to': self.translator.DEFAULT_LANGUAGE,
                'from': 'fr',
            }
        )
        request_get.return_value.raise_for_status.assert_called_with()
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value='super-token')
    @patch('requests.get', return_value=MagicMock(
        content='<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">I am tired</string>'
    ))
    def test_translate_API_error(self, request_get, get_access_token):
        resp = request_get.return_value
        resp.raise_for_status.side_effect = HTTPError(
            'boom', response=MagicMock(content="<xml>OUPS</xml>"), request='req'
        )
        with self.assertRaises(errors.AzureApiError):
            self.translator.translate(text='Je suis fatigué')
        request_get.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/xml',
            },
            params={
                'text': 'Je suis fatigué',
                'to': self.translator.DEFAULT_LANGUAGE,
            }
        )
        resp.raise_for_status.assert_called_with()
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value='super-token')
    @patch('requests.get', return_value=MagicMock(
        content='oupsie'
    ))
    def test_translate_not_an_xml(self, request_get, get_access_token):
        with self.assertRaises(errors.AzureApiBadFormatError):
            self.translator.translate(text='Je suis fatigué')
        request_get.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/xml',
            },
            params={
                'text': 'Je suis fatigué',
                'to': self.translator.DEFAULT_LANGUAGE,
            }
        )
        request_get.return_value.raise_for_status.assert_called_with()
        get_access_token.assert_called_with()



class ErrorsTestCase(unittest.TestCase):

    def test_BaseAzureException_init(self):
        exc = errors.BaseAzureException("youpi")
        self.assertIsNone(exc.response)
        self.assertIsNone(exc.request)
        self.assertEqual(str(exc), 'youpi')

    def test_BaseAzureException_init_with_response_and_request(self):
        exc = errors.BaseAzureException("youpi", response="resp", request="req")
        self.assertEqual(exc.response, "resp")
        self.assertEqual(exc.request, "req")
        self.assertEqual(str(exc), 'youpi')

    def test_AzureApiError_init(self):
        exc = errors.AzureApiError("oups")
        self.assertIsNone(exc.response)
        self.assertIsNone(exc.request)
        self.assertEqual(str(exc), 'oups')

    def test_AzureApiError_init_parsing_response(self):
        resp = Response()
        resp.status_code = 400
        resp._content = (
            "<html><body><h1>Argument Exception</h1><p>Method: Translate()</p>"
            "<p>Parameter: from</p><p>Message: 'from' must be a valid language&#xD;"
            "\nParameter name: from</p><code></code>"
            "<p>message id=0243.V2_Rest.Translate.49CC880B</p></body></html>"
        )
        exc = errors.AzureApiError("oups", response=resp)
        self.assertIsNotNone(exc.response)
        self.assertEqual(
            str(exc),
            "HTTP status: 400; "
            "Argument Exception; Method: Translate(); "
            "Parameter: from; "
            "Message: 'from' must be a valid language; Parameter name: from; "
            "message id=0243.V2_Rest.Translate.49CC880B"
        )

    def test_AzureApiError_init_parsing_response_error(self):
        resp = Response()
        resp.status_code = 400
        resp._content = "eazoieoiazbeoazgeoaziub"
        exc = errors.AzureApiError("stuff", response=resp)
        self.assertEqual(str(exc), "stuff")
