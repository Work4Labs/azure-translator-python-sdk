# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import unittest

from mock import patch, MagicMock
from requests.exceptions import HTTPError

from azure_translator import Translator, AzureApiError, AzureApiBadFormatError


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
        resp.raise_for_status.side_effect = HTTPError('boom', response='resp', request='req')
        with self.assertRaises(AzureApiError):
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
        content='<string xmlns="http://schemas.microsoft.com/2003/10/Serialization/">Je suis fatigué</string>'
    ))
    def test_translate_custom_language(self, request_get, get_access_token):
        self.assertEqual(self.translator.translate(text='I am tired', to='fr'), 'Je suis fatigué')
        request_get.assert_called_with(
            self.translator.TRANSLATE_API,
            headers={
                'Authorization': 'Bearer super-token',
                'Accept': 'application/xml',
            },
            params={
                'text': 'I am tired',
                'to': 'fr',
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
        resp.raise_for_status.side_effect = HTTPError('boom', response='resp', request='req')
        with self.assertRaises(AzureApiError):
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
        with self.assertRaises(AzureApiBadFormatError):
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
