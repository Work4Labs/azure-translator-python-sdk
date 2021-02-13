# -*- coding: utf-8 -*-

import unittest

from mock import patch, MagicMock
from requests.exceptions import HTTPError, Timeout
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
            },
            timeout=Translator.HTTP_TIMEOUT
        )

    @patch('requests.post')
    def test_get_access_token_error(self, request_post):
        resp = request_post.return_value
        resp.raise_for_status.side_effect = HTTPError(
            'boom', response=MagicMock(content="OUPS"), request='req'
        )
        with self.assertRaises(errors.AzureCannotGetTokenError):
            self.translator.get_access_token()
        request_post.assert_called_with(
            self.translator.TOKEN_API,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/jwt',
                'Ocp-Apim-Subscription-Key': 'some-api-key',
            },
            timeout=Translator.HTTP_TIMEOUT
        )

    @patch('requests.post', side_effect=Timeout)
    def test_get_access_token_timeout(self, request_post):
        with self.assertRaises(errors.AzureApiTimeoutError):
            self.translator.get_access_token()
        request_post.assert_called_with(
            self.translator.TOKEN_API,
            headers={
                'Content-Type': 'application/json',
                'Accept': 'application/jwt',
                'Ocp-Apim-Subscription-Key': 'some-api-key',
            },
            timeout=Translator.HTTP_TIMEOUT
        )

    @patch.object(Translator, 'get_access_token', return_value=b'super-token')
    @patch('requests.Response.json', return_value=[{"translations": [{"text": "I am tired"}]}])
    @patch('requests.post')
    def test_translate(self, request_post, response_json, get_access_token):
        request_post.return_value = MagicMock(json=response_json)

        self.assertEqual(self.translator.translate(text='Je suis fatigué'), 'I am tired')
        request_post.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/json',
                'Content-type': 'application/json',
            },
            timeout=Translator.HTTP_TIMEOUT,
            params={
                'to': self.translator.DEFAULT_LANGUAGE,
            },
            json=[{'text': 'Je suis fatigué'}]
        )
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value=b'super-token')
    @patch('requests.Response.json', return_value=[{"translations": [{"text": "Je suis"}]}])
    @patch('requests.post')
    def test_translate_custom_language(self, request_post, response_json, get_access_token):
        request_post.return_value = MagicMock(json=response_json)
        self.assertEqual(self.translator.translate(text='I am', to='fr'), 'Je suis')
        request_post.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/json',
                'Content-type': 'application/json',
            },
            timeout=Translator.HTTP_TIMEOUT,
            params={
                'to': 'fr',
            },
            json=[{'text': 'I am'}],
        )
        get_access_token.assert_called_with()


    @patch.object(Translator, 'get_access_token', return_value=b'super-token')
    @patch('requests.Response.json', return_value=[{"translations": [{"text": "fatigué"}]}])
    @patch('requests.post')
    def test_translate_response_encoding(self, request_post, response_json, get_access_token):
        request_post.return_value = MagicMock(json=response_json)
        self.assertEqual(self.translator.translate(text='tired', to='fr'), 'fatigué')
        request_post.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/json',
                'Content-type': 'application/json',
            },
            timeout=Translator.HTTP_TIMEOUT,
            params={
                'to': 'fr',
            },
            json=[{'text': 'tired'}],
        )
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value=b'super-token')
    @patch('requests.Response.json', return_value=[{"translations": [{"text": "I am tired"}]}])
    @patch('requests.post')
    def test_translate_source_lang(self, request_post, response_json, get_access_token):
        request_post.return_value = MagicMock(json=response_json)
        self.assertEqual(self.translator.translate(text='Je suis fatigué', source_language='fr'), 'I am tired')
        request_post.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/json',
                'Content-type': 'application/json',
            },
            json=[{'text': 'Je suis fatigué'}],
            timeout=Translator.HTTP_TIMEOUT,
            params={
                'to': self.translator.DEFAULT_LANGUAGE,
                'from': 'fr',
            }
        )
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value=b'super-token')
    @patch('requests.post', return_value=MagicMock(return_value=[{"translations": [{"text": "I am tired"}]}]))
    def test_translate_API_error(self, request_post, get_access_token):
        resp = request_post.return_value
        resp.raise_for_status.side_effect = HTTPError(
            'boom', response=MagicMock(content="OUPS"), request='req'
        )
        with self.assertRaises(errors.AzureApiError):
            self.translator.translate(text='Je suis fatigué')
        request_post.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/json',
                'Content-type': 'application/json',
            },
            timeout=Translator.HTTP_TIMEOUT,
            params={
                'to': self.translator.DEFAULT_LANGUAGE,
            },
            json=[{'text': 'Je suis fatigué'}]
        )
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value=b'super-token')
    @patch('requests.Response.json', return_value='OUPS')
    @patch('requests.post')
    def test_translate_not_a_json(self, request_post, response_json, get_access_token):
        request_post.return_value = MagicMock(raise_for_status=MagicMock(return_value='200'), json=response_json)
        with self.assertRaises(errors.AzureApiBadFormatError):
            self.translator.translate(text='Je suis fatigué')
        request_post.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/json',
                'Content-type': 'application/json',
            },
            timeout=Translator.HTTP_TIMEOUT,
            params={
                'to': self.translator.DEFAULT_LANGUAGE,
            },
            json=[{'text': 'Je suis fatigué'}]
        )
        get_access_token.assert_called_with()

    @patch.object(Translator, 'get_access_token', return_value=b'super-token')
    @patch('requests.post', side_effect=Timeout)
    def test_translate_timeout_error(self, request_post, get_access_token):
        resp = request_post.return_value
        resp.raise_for_status.side_effect = HTTPError(
            'boom', response=MagicMock(content="OUPS"), request='req'
        )
        with self.assertRaises(errors.AzureApiTimeoutError):
            self.translator.translate(text='Je suis fatigué')
        request_post.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Content-type' : 'application/json',
                'Authorization': 'Bearer super-token',
                'Accept': 'application/json',
            },
            timeout=Translator.HTTP_TIMEOUT,
            params={
                'to': self.translator.DEFAULT_LANGUAGE,
            },
            json=[{'text': 'Je suis fatigué'}]
        )
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
            "Argument Exception; Method: Translate(); "
            "Parameter: from; "
            "Message: 'from' must be a valid language; Parameter name: from; "
            "message id=0243.V2_Rest.Translate.49CC880B"
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
        self.assertNotEqual(str(exc), "stuff")
