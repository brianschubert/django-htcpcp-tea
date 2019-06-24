.. This file is distributed under the MIT License. If a copy of the
.. MIT License was not distributed with this file, you can obtain one
.. at https://opensource.org/licenses/MIT.

Installation
============

Getting the package
-------------------

.. note::

    Regardless of the installation method that you choose, it is recommended that you use a virtual environment to keep you Python environment clean. If you are using Python 3.6 or greater, the tools you will to create virtual environments ship with the interpreter as the `venv`_ module. For older versions of Python, or for further customization, see the `virtualenv`_ and `virtualenvwrapper`_ packages.

.. _venv: https://docs.python.org/3.6/library/venv.html
.. _virtualenv: https://pypi.org/project/virtualenv/
.. _virtualenvwrapper: https://pypi.org/project/virtualenvwrapper/


The recommended way to install django-htcpcp-tea is via `pip`_:

.. _pip: https://pip.pypa.io/en/stable/

.. code-block:: console

    $ pip install django-htcpcp-tea

Alternatively, you can install django-htcpcp-tea from its source:

.. code-block:: console

    $ git clone git://github.com/blueschu/django-htcpcp-tea.git
    $ cd django-htcpc-tea
    $ python3 setup.py install


Installing the Django App
-------------------------

Add ``'django_htcpcp_tea'`` to your ``INSTALLED_APPS`` setting:

.. code-block:: python

    INSTALLED_APPS = [
        # ...
        'django_htcpcp_tea',
        # ...
    ]

If you intend to use interactive pot sessions, make sure that the `Django sessions framework`_ is also installed and properly configured (it's installed by default).

.. _Django sessions framework: https://docs.djangoproject.com/en/2.2/topics/http/sessions/

Then, enable the django-htcpcp-tea middleware in your settings:

.. code-block:: python

    MIDDLEWARE = [
        # ...
        'django_htcpcp_tea.middleware.HTCPCPTeaMiddleware',
        # ...
    ]


And finally, update your project's URLconf to include the HTCPCP urls:

.. code-block:: python

    from django.urls import include, path

    urlspatterns = [
        # ...
        path('htcpcp/', include('django_htcpcp_tea.urls')),
        # ...
    ]
