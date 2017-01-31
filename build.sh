#!/usr/bin/env bash
rm -r build/ dist/ azure_translator.egg-info/
python setup.py bdist_egg
python setup.py sdist
