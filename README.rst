Django HTCPCP-TEA
=================

.. image:: https://travis-ci.com/blueschu/django-htcpcp-tea.svg?branch=master
    :target: https://travis-ci.com/blueschu/django-htcpcp-tea
    :alt: Travis CI Build

.. image:: https://coveralls.io/repos/github/blueschu/django-htcpcp-tea/badge.svg?branch=master
    :target: https://coveralls.io/github/blueschu/django-htcpcp-tea?branch=master
    :alt: Coverage

.. image:: https://readthedocs.org/projects/django-htcpcp-tea/badge/?version=latest
    :target: https://django-htcpcp-tea.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

.. image:: https://img.shields.io/pypi/pyversions/django-htcpcp-tea.svg
    :target: https://pypi.org/project/django-htcpcp-tea/
    :alt: PyPI - Python Version

.. image:: https://img.shields.io/pypi/djversions/django-htcpcp-tea.svg
    :target: https://pypi.org/project/django-htcpcp-tea/
    :alt: PyPI - Django Version

.. image:: https://img.shields.io/github/license/blueschu/django-htcpcp-tea.svg
    :target: ./LICENSE
    :alt: License

..

    [T]here is a strong, dark, rich requirement for a protocol designed
    espressoly for the brewing of coffee.

    --- RFC 2324 Section 1

A `Django`_ app that implements the TEA extension to HTCPCP as defined in `RFC 7168`_.

This app extends the Django web framework to simulate the functionality of an HTCPCP server. Both the HTCPCP/1.0 protocol from `RFC 2324`_ and the HTCPCP-TEA protocol from `RFC 7168`_ are supported.

.. _RFC 7168: https://tools.ietf.org/html/rfc7168
.. _Django: https://www.djangoproject.com/
.. _RFC 2324: https://tools.ietf.org/html/rfc2324

Notable features:

- Customizable coffee and teapots
- Support for BREW and WHEN HTTP methods
- Interactive brewing sessions
- HTCPCP response codes (e.g. 418 I'm a teapot)
- User-defined forbidden combinations of beverage additions

Documentation
-------------

Documentation for Django HTCPCP-TEA is available on `Read the Docs`_.

.. _Read the Docs: https://django-htcpcp-tea.readthedocs.io/en/latest/?badge=latest

References
----------

- `[RFC 2324] Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0)`_
- `[RFC 7158] The Hyper Text Coffee Pot Control Protocol for Tea Efflux Appliances (HTCPCP-TEA)`_
- `[RFC 2295] Transparent Content Negotiation in HTTP`_
- `MDN Web Docs | HTTP response codes`_

.. _[RFC 2324] Hyper Text Coffee Pot Control Protocol (HTCPCP/1.0): https://tools.ietf.org/html/rfc2324
.. _[RFC 7158] The Hyper Text Coffee Pot Control Protocol for Tea Efflux Appliances (HTCPCP-TEA): https://tools.ietf.org/html/rfc7168
.. _[RFC 2295] Transparent Content Negotiation in HTTP: https://tools.ietf.org/html/rfc2295
.. _MDN Web Docs | HTTP response codes: https://developer.mozilla.org/en-US/docs/Web/HTTP/Status

Related Work
------------

- Shane Brunswick's `Save 418 Movement`_.
- Dash Winterson's `HTCPCP Middleware (django-htcpcp)`_

.. _Save 418 Movement: http://save418.com/
.. _HTCPCP Middleware (django-htcpcp): https://github.com/dashdanw/django-htcpcp

License
-------

This software is licensed under the `MIT License`_. For more
information, read the file `LICENSE`_.

.. _MIT License: https://opensource.org/licenses/MIT
.. _LICENSE: ./LICENSE
