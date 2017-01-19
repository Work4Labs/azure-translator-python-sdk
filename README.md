# azure-translator-python-sdk

[![CircleCI](https://circleci.com/gh/Work4Labs/azure-translator-python-sdk/tree/master.svg?style=shield&circle-token=d06ed7a66ca3c1565f4defd3ca8f4fe6137008a6)](https://circleci.com/gh/Work4Labs/azure-translator-python-sdk/tree/master)
[![PyPI version](https://badge.fury.io/py/azure-translator.svg)](https://badge.fury.io/py/azure-translator)
![License](https://img.shields.io/pypi/l/azure-translator.svg)

For more information on Azure translator API, follow
[their documentation](http://docs.microsofttranslator.com/text-translate.html#!/default/get_Translate).

Usage:
```python
>>> from azure_translator import Translator

>>> t = Translator('your_api_key')
>>> t.translate('Je suis fatigué')
'I am tired'

>>> t.translate("Hello", to='fr')
'Bonjour'

>>> t.translate("Aujourd'hui", source_language='fr')
'Today'
```
