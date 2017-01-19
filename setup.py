#!/usr/bin/env python
from setuptools import setup
import os


def read(fname):
    """
    Read file (README).
    """
    try:
        with open(os.path.join(os.path.dirname(__file__), fname)) as handle:
            return handle.read()
    except IOError:
        return ''


setup(
    name='azure-translator',
    version='0.1.1',
    description='Python SDK for Azure Translator API.',
    long_description=read('README.md'),
    author='mvdb',
    author_email='mvdb@work4labs.com',
    url='https://github.com/Work4Labs/azure-translator-python-sdk',
    packages=['azure_translator'],
    license='Apache',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
    ],
    install_requires=[
        "requests>=2.12.0",
    ],
    test_suite='nose.collector',
    tests_require=[
        'mock',
        'nose'
    ]
)
