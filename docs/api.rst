.. This file is distributed under the MIT License. If a copy of the
.. MIT License was not distributed with this file, you can obtain one
.. at https://opensource.org/licenses/MIT.

Django HTCPCP-TEA API
=====================

Below is an extremely terse summary of the API exposed by Django HTCPCP-TEA.

Models (``django_htcpcp_tea.models``)
-------------------------------------

.. autoclass:: django_htcpcp_tea.models.Pot
    :members: tea_capable, is_teapot, fetch_additions

    .. py:attribute:: name

        The name of this pot, e.g. "Joe\'s Joe Jar" or "Breville (R) BTM800XL"

    .. py:attribute:: brew_coffee

        Whether this pot can brew coffee.

    .. py:attribute:: supported_teas

        The types of tea that this pot can brew. May be empty.

    .. py:attribute:: supported_additions

        The beverage additions that this pot supported. May be empty.

.. autoclass:: django_htcpcp_tea.models.TeaType

    .. py:attribute:: name

       The name of this tea type.

    .. py:attribute:: slug

       The URL slug identifying this tea type.

.. autoclass:: django_htcpcp_tea.models.Addition
    :members: MILK, SYRUP, SWEETENER, SPICE, ALCOHOL, SUGAR, OTHER, is_milk
    :undoc-members:

    .. py:attribute:: name

       The name of this beverage addition as it would appear in the
       HTCPCP Accept-Additions header field.

    .. py:attribute:: type

       The type of this additions

.. autoclass:: django_htcpcp_tea.models.ForbiddenCombination
    :members: forbids_additions

    .. py:attribute:: tea

       The type of tea that this forbidden combination applies to. If null, this forbidden combination applies to all beverages.

    .. py:attribute:: additions

       The combination of additions that this forbidden combination forbids.

Views (``django_htcpcp_tea.views``)
-----------------------------------

.. automodule:: django_htcpcp_tea.views
    :members:
    :undoc-members:


Decorators (``django_htcpc_tea.decorators``)
--------------------------------------------

.. automodule:: django_htcpcp_tea.decorators
    :members:

Settings (``django_htcpcp_tea.settings``)
-----------------------------------------

.. automodule:: django_htcpcp_tea.settings
    :members:
    :private-members:
    :undoc-members:

    .. autodata:: htcpcp_settings
        :annotation: = _HTCPCPTeaSettings('HTCPCP')

        Access to the Django HTCPCP-TEA settings should be done through
        this instance.


Utils (``django_htcpcp_tea.utils``)
-----------------------------------

.. automodule:: django_htcpcp_tea.utils
    :members:
