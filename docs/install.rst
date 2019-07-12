.. This file is distributed under the MIT License. If a copy of the
.. MIT License was not distributed with this file, you can obtain one
.. at https://opensource.org/licenses/MIT.

Installation
============

Getting the package
-------------------

.. note::

    Regardless of the installation method that you choose, it is recommended that you use a virtual environment to keep your Python environment clean. If you are using Python 3.6 or greater, the tools you will to create virtual environments ship with the interpreter as the `venv`_ module. For older versions of Python, or for further customization, see the `virtualenv`_ and `virtualenvwrapper`_ packages.

.. _venv: https://docs.python.org/3.6/library/venv.html
.. _virtualenv: https://pypi.org/project/virtualenv/
.. _virtualenvwrapper: https://pypi.org/project/virtualenvwrapper/


The recommended way to install Django HTCPCP-TEA is via `pip`_:

.. _pip: https://pip.pypa.io/en/stable/

.. code-block:: console

    $ pip install django-htcpcp-tea

Alternatively, you can install Django HTCPCP-TEA from its source:

.. code-block:: console

    $ git clone git://github.com/blueschu/django-htcpcp-tea.git
    $ cd django-htcpcp-tea
    $ python3 setup.py install


Installing the Django App
-------------------------

To load Django HTCPCP-TEA into an existing Django project, add ``'django_htcpcp_tea'`` to the ``INSTALLED_APPS`` list in your setting file:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_htcpcp_tea',
        # ...
    ]

If you intend to use interactive pot sessions, make sure that the `Django sessions framework`_ is also installed and properly configured (it's installed by default).

.. _Django sessions framework: https://docs.djangoproject.com/en/2.2/topics/http/sessions/

Next, enable the Django HTCPCP-TEA middleware in your settings:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'django_htcpcp_tea.middleware.HTCPCPTeaMiddleware',
        # ...
    ]

Configuring the URL patterns
----------------------------

It is recommend to install the URL configuration for Django HTCPCP-TEA in one of two fashions: the "Standard" Installation, where this app behaves like a standard Django app and is isolated to the URL namespace you include it under, or the "Schema Compliant" Installation, which makes this app work extra hard to follow the HTCPCP URI schema.

Standard Installation
^^^^^^^^^^^^^^^^^^^^^

You can include the Django HTCPCP-TEA urls in your URL configuration in the same way as any Django app:

.. code-block:: python

    from django.urls import include, path

    urlspatterns = [
        # ...
        path('htcpcp/', include('django_htcpcp_tea.urls')),
        # ...
    ]

With this installation method, all HTCPCP URIs must be prefixed with the string ``/htcpcp``. For example, the request line a of BREW request to Pot #1 would look like

.. code-block:: http

    BREW /htcpcp/pot-1/ HTTP/1.1

Schema Compliant Installation
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

For an installation that closely follows that HTCPCP standard, append the Django HTCPCP-TEA URLs directly to your URL patterns:

.. code-block:: python

    from django.urls import include, path
    from django_htcpcp_tea import urls as htcpcp_urls

    urlspatterns = [
        # ...
    ]

    urlpatterns += htcpcp_urls.urlpatterns

Then, add the following options to your project's Django settings file:

.. code-block:: python

    HTCPCP_OVERRIDE_ROOT_URI = True

This will allow Django HTCPCP-TEA to override default URL dispatcher when it receives a request that is unambiguously an HTCPCP request. Making requests to the root url (``/``) or top-level HTCPCP URIs (e.g. ``/pot-1/earl-grey/``) will behave as defined in RFCs 2324 and 7168 with no ``/htcpcp`` prefix required.

(Optional) Loading the demo data fixture
----------------------------------------

Django HTCPCP-TEA ships will a few data fixtures to help you explore the app after installation:

- ``rfc_2324_additions``: All of the beverage additions types listed as examples in RFC 2324.
- ``rfc_7168_additions``: The Sugar addition types added to the HTCPCP standard in RFC 7168.
- ``rfc_7168_teas``: The tea types listed as examples in RFC 7168.
- ``demo_pots``: A hand-craft selection of coffee- and teapots to demonstrate the HTCPCP protocol (depends on ``rfc_2324_additions`` and ``rfc_7168_teas``).
- ``demo_forbidden_combinations``: Common sense rules that forbid combinations of additions contrary to the sensibilities of a consensus of drinkers (depends on ``rfc_2324_additions`` and ``rfc_7168_teas``).

Each of these data fixtures can be loaded using the following `manage.py`_ command:

.. code-block:: console

    $ ./manage.py loaddata FIXTURE

.. _manage.py: https://docs.djangoproject.com/en/2.2/ref/django-admin/
