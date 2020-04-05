#!/usr/bin/env python
# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from setuptools import setup, find_packages
try:
    from pypandoc import convert
except ImportError:
    import io

    def convert(filename, fmt):
        with io.open(filename, encoding='utf-8') as fd:
            return fd.read()

CLASSIFIERS = [
    'Environment :: Web Environment',
    'Framework :: Django',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 2.7',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'Topic :: Software Development :: Libraries :: Application Frameworks',
    'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
]

setup(
    author="Bart Pijnenburg",
    author_email="bpijn@outlook.com",
    name='djangoshop-mollie',
    version=0.1,
    description='Mollie Payment Provider plug-in for django-shop',
    long_description=convert('README.md', 'rst'),
    url='https://github.com/bartpijn/djangoshop-mollie',
    license='MIT License',
    platforms=['OS Independent'],
    classifiers=CLASSIFIERS,
    install_requires=[
        'mollie-api-python>=2.3.1,<3.0.0',
    ],
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
)