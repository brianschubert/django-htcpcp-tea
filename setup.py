#!/usr/bin/env python3
#  Copyright (c) 2019 Brian Schubert
#
#  This file is distributed under the MIT License. If a copy of the
#  MIT License was not distributed with this file, you can obtain one
#  at https://opensource.org/licenses/MIT.

from setuptools import find_packages, setup

with open('README.rst') as readme:
    long_description = readme.read()

CLASSIFIERS = [
    'Development Status :: 3 - Alpha',
    'Environment :: Web Environment',
    'Framework :: Django',
    'Framework :: Django :: 2.0',
    'Framework :: Django :: 2.1',
    'Framework :: Django :: 2.2',
    'Intended Audience :: Developers',
    'License :: OSI Approved :: MIT License',
    'Operating System :: OS Independent',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    "Topic :: Internet :: WWW/HTTP",
    "Topic :: Software Development :: Libraries :: Python Modules",
]

setup(
    name='django-htcpcp-tea',
    version='0.1.0',
    packages=find_packages(),
    license='MIT',
    author='Brian Schubert',
    url='https://github.com/blueschu/django-htcpcp-tea',
    description="Django app implementing HTCPCP-TEA as defined in RFC 7168.",
    long_description=long_description,
    long_description_content_type='text/x-rst',
    keywords="htcpcp django rfc-2324 rfc-7168 coffee tea",
    classifiers=CLASSIFIERS,
    install_requires=['django>=2.0'],
    python_requires='>=3',
)
