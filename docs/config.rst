.. This file is distributed under the MIT License. If a copy of the
.. MIT License was not distributed with this file, you can obtain one
.. at https://opensource.org/licenses/MIT.

Configuration
=============

Settings
--------

HTCPCP_ALLOW_DEPRECATED_POST
^^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

Whether to allow clients to use the POST method for brewing requests.

The use of the POST method for HTCPCP requests is officially deprecated in `RFC 2324 section 2.1.1`_. However, the standard also stipulates that, HTCPCP servers must accept POST and BREW requests equivalently, and so setting this configuration to ``False`` is not recommended.

.. _RFC 2324 section 2.1.1: https://tools.ietf.org/html/rfc2324#section-2.1.1

HTCPCP_CHECK_FORBIDDEN
^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

Whether to check for forbidden addition combinations as defined in `RFC 7168 seciton 2.3.2`_.

When set to ``True``, clients will receive a 403 Forbidden with an explanatory message upon requesting a forbidden addition combination.

.. _RFC 7168 seciton 2.3.2: https://tools.ietf.org/html/rfc7168#section-2.3.2

HTCPCP_DISABLE_CSRF
^^^^^^^^^^^^^^^^^^^

Default: ``True``

When set to ``True``, this app's views will be exempt from `Django's CSRF protection`_.

In order for HTCPCP requests to pass the CSRF checks, clients would need to set valid Referrer headers and correctly store and transmit CSRF tokens. For most use cases, this is an unnecessary burden, and so these checks are disabled by default.

If you set this configuration to ``False``, you will need to update the templates to include CSRF tokens and ensure that your clients know to include the required headers and data in their requests.

.. _Django's CSRF protection: https://docs.djangoproject.com/en/2.2/ref/csrf/

HTCPCP_GET_ADDITIONS
^^^^^^^^^^^^^^^^^^^^

Default: ``True``

When set to ``True``, clients will be able to request beverage additions by listing additions after the ``?`` in a url.

The URI scheme specified in `RFC 2324 section 3`_ suggests that beverage additions can be provided as list in the query string of the request uri. When this setting is enabled, additions requested in the Accept-Additions header and in the query string are given equal precedence.

Do note that setting this configuration to ``True`` may enable CSBF (Cross-Site Beverage Forgery) attacks as HTCPCP urls could contain malicious beverage additions that will be requeted with the client knowledge (such as Sea-Salt).

Setting this option to ``True`` *does not* enable HTCPCP GET requests.

.. _RFC 2324 section 3: https://tools.ietf.org/html/rfc2324#section-3


HTCPCP_OVERRIDE_SERVER_NAME
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

Whether to override the ``Server`` header field for HTCPCP requests.

When set to ``True``, the Server header will be set to ``'HTCPCP-TEA {SERVER_SOFTWARE}'``, where ``{SERVER_SOFTWARE}`` is the server software string that is added to the environment by a WSGI server, such as the `reference WSGI implementation`_ used by the Django testing server.

When set to a callable, the provided callable will be invoked with the request and response objects received by the middleware. The return value will used as the Server header.

Example:

.. code-block:: python

    def HTCPCP_OVERRIDE_SERVER_NAME(request, response):
        import sys
        from platform import python_implementation

        return 'Teapot {}/{}'.format(
            python_implementation(),
            sys.version.split()[0],
        )

When set to a string, the provided string will be formatted with all of the context from ``request.META``.


.. _reference WSGI implementation: https://docs.python.org/3.7/library/wsgiref.html#wsgiref.handlers.BaseHandler.server_software


HTCPCP_POT_SESSIONS
^^^^^^^^^^^^^^^^^^^

Default: ``True``

Whether to track user interactions with the server's pots using the `Django session framework`_.

When set to ``True``, this app will track when beverage a particular user from each pot to enable statefull interactions with the server. Clients will need to follow a complete HTCPCP request cycle, including a start, stop, and optional 'WHEN' request for each beverage the client requests. Invalid HTCPC request sequences (such as requesting a new beverage in a pot that is already brewing a beverage) will result in errors.

When set to ``False``, this app will naively simulate an HTCPCP server without tracking user sessions. Start, stop, and 'WHEN' requests will be accepted even if their ordering is not logical (e.g. saying 'WHEN' before requesting any beverage).

.. _Django session framework: .. _Django sessions framework: https://docs.djangoproject.com/en/2.2/topics/http/sessions/

HTCPCP_STRICT_MIME_TYPE
^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

When set to ``True``, HTCPCP requests will be ignored unless they have a content type of either ``message/coffeepot`` or ``message/teapot``.

Set this configuration to ``False`` if modifying HTTP Content-Type header for HTTP requests is not convenient for your use case.

STRICT_REQUEST_BODY
^^^^^^^^^^^^^^^^^^^

Default: ``False``

When set to ``True``, HTCPCP requests must have a body constistly solely of ``start`` or ``stop``.

By default, this configuration is set to ``False`` since it is understood that some clients may want to include additional content in the request entity, such as "please" and "thank you".
