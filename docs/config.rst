.. This file is distributed under the MIT License. If a copy of the
.. MIT License was not distributed with this file, you can obtain one
.. at https://opensource.org/licenses/MIT.

Configuration
=============

Django HTCPCP-TEA offers a few mechanisms to customize the behavior of your HTCPCP service.

Settings
--------

Each of the follow settings can be configured in your project's `settings module`_ to control the behavior of Django HTCPCP-TEA.

.. _settings module: https://docs.djangoproject.com/en/2.2/topics/settings/

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


HTCPCP_OVERRIDE_ROOT_URI
^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

Whether to override the the root URI (``/``) for HTCPCP requests.

This option is included to allow for the creation of highly compliant HTCPCP services. Setting this option to ``True`` will allow your webapp to serve a proper Alternates header and page when an HTCPCP request is directed to the root URI (see `RFC 7168 section 2.1.1`_). This is equivalent to requesting the ``''`` URI specified in this app's URL patterns.

Since overriding the root page of a webapp can be a surprising behavior, enabling ``HTCPCP_OVERRIDE_ROOR_URI`` requires opting-in to stricter HTCPCP validation checks to make sure clients _really_ want a root request to be treated as an HTCPCP request. Namely, the ``HTCPCP_STRICT_MINE_TYPES`` setting MUST also be enabled in order for this setting to have an effect.

.. _RFC 7168 section 2.1.1: https://tools.ietf.org/html/rfc7168#section-2.1.1


HTCPCP_OVERRIDE_SERVER_NAME
^^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

Whether to override the ``Server`` header field for HTCPCP requests.

When set to ``True``, the Server header will be set to ``'HTCPCP-TEA {SERVER_SOFTWARE}'``, where ``{SERVER_SOFTWARE}`` is the server software string that is added to the environment by a WSGI server, such as the `reference WSGI implementation`_ used by the Django testing server. If the environment providess no ``{SERVER_SOFTWARE}``, then the string ``Python`` will be used.

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

HTCPCP_STRICT_REQUEST_BODY
^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``False``

When set to ``True``, HTCPCP requests must have a body constistly solely of ``start`` or ``stop``.

By default, this configuration is set to ``False`` since it is understood that some clients may want to include additional content in the request entity, such as "please" and "thank you".


HTCPCP_USE_SAFE_HEADER_EXT
^^^^^^^^^^^^^^^^^^^^^^^^^^

Default: ``True``

Whether to use the extension to the ``Safe`` header field  defined in `RFC 2324 section 2.2.1.1`_.

When set to ``True``, the decorators that this app provides for managing the ``Safe`` header will modify the header's value according to its extended semantics in the HTCPCP standard.

.. _RFC 2324 section 2.2.1.1: https://tools.ietf.org/html/rfc2324#section-2.2.1.1


Templates
---------

The default templates provided by Django HTCPCP-TEA are designed to be minimal so that HTCPCP responses are readable from a terminal window.

All of the templates used by Django HTCPCP-TEA live in the template directory ``templates/django_htcpcp_tea``, including the error code templates such as ``403.html``. The one exceptions to this is the 404 response code, for which the root 404 template is used to help HTCPCP services "blend in" with the normal functionality of a web app.

base.html
^^^^^^^^^

The base template for all HTCPCP templates. Override this template if you would like to incorporate your HTCPCP instances into the natural flow of your web app.

This template must define a single block, ``htcpcp_content``, which is where all HTCPCP related content is placed by default.

base_beverage.html
^^^^^^^^^^^^^^^^^^

The base template for successful brewing sequences. By default, this template mirrors ``base.html``.


brewing.html
^^^^^^^^^^^^

The template used when a pot successfully begins brewing a new beverage.

Context variables:

- |var_pot|
- |var_beverage|
- |var_additions|

If the request resulted in a new pot of coffee being brew, the following context variable will also be made available in order to comply with RFC 7168 section 2.1.1:

- |var_alternatives|


finished.html
^^^^^^^^^^^^^

The template used when a pot successfully finishes brewing a beverage.

Context variables:

- |var_pot|
- |var_beverage|
- |var_additions|


options.html
^^^^^^^^^^^^

The template used to display a list of beverage options when brewing does not begin.

This template will be used when an HTCPCP request is made to the root URI, or when a request is made of a specific pot with the ``message/teapot`` content type.

Context variables:

- ``alternatives``:


pouring.html
^^^^^^^^^^^^

The template used when a pot begins to poour milk into a beverage.

Inserting relevant graphics into this templates is *highly* recommended.

Context variables:

- |var_pot|
- |var_beverage|
- |var_additions|


base_error.html
^^^^^^^^^^^^^^^

The base template for all HTCPCP errors.

This template must define two template blocks: ``error_title`` and ``error_body``.


400.html
^^^^^^^^

The template used for HTCPCP requests with invalid semantics, such as starting a beverage with a ``WHEN`` request, or attempting to start a new beverage while milk is being poured.

Context variables:

- ``error_reason``: An error message explaining why the client's request was not valid.
- |var_pot|
- |var_beverage|
- |var_additions|

.. note::

    If the error was due to the client using a ``WHEN`` request with a ``start`` body, the ``pot``, ``beverage``, and ``additions`` context variables will *not* be available.


403.html
^^^^^^^^

The template used when a forbidden combination of additions is requested.

Context variables:

- ``matched_combinations``: The ForbiddenCombination instances that prohibit some part of the requested additions

406.html
^^^^^^^^

The template used when unsupported beverage additions are requested.

Context variables:

- ``supported_additions``: The Addition instances that are supported by the pot in question.

418.html
^^^^^^^^

The template used when a client attempts to brew coffee in a teapot.

No context variables are made available.

503.html
^^^^^^^^

The template used when the beverage request cannot be serviced due to the current state of the pot.

Context variables:

- ``error_reason``: An error message explaining why the client's request could not be serviced.

If this error occurs due to a new beverage being requested while a pot is busy, the following context variables will also be made available:

- |var_pot|
- |var_beverage|
- |var_additions|

includes/additions.html
^^^^^^^^^^^^^^^^^^^^^^^

The template used to render lists of beverage additions.

Context variables:

- ``additions``: The Addition instances to be rendered.

includes/alternatives.html
^^^^^^^^^^^^^^^^^^^^^^^^^^

The template used to render lists of beverage alternatives.

Context variables:

- ``alternatives``: The (uri, content-type) pairs of available alternate beverages to be rendered.


.. |var_pot| replace:: ``pot``: The Pot model that the request was directed to.
.. |var_beverage| replace:: ``beverage``: The name of the beverage being brewed.
.. |var_additions| replace:: ``additions``: The additions that were requested for the beverage.
.. |var_alternatives| replace:: ``alternatives``: The (uri, content-type) pairs for the available alternate beverages.
