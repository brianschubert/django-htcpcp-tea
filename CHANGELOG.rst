Changes
=======

For complete record of changes, see the commit log of the `public git repository`_.

.. _public git repository: https://github.com/blueschu/django-htcpcp-tea

v0.8.0
----------

- Migrated build system from ``setuptools`` to ``poetry``.
- Upgraded supported Python versions from 3.4-3.8 to 3.8+.
- Development: use black formatting and isort import ordering.

v0.7.0
------

Released 2019-08-29

- Add initial example usage documentation
- Add setting to override MIME type for HTCPCP responses
- Add PyPI package version badge to README
- Add Python 3.8 dev build to Travis-CI config
- Change PyPI development status classifier to Beta
- Fix server name being overridden for non-HTCPCP requests
- Remove explicit module names from API documentation
- Remove supported Python and Django version badges from README

v0.6.0
------

Released 2019-07-14

- Add units tests for ``middleware`` module
- Add units test for ``admin`` module
- Add check to strictly enforce HTCPCP MIME types
- Add setting to override the rot url view for HTCPCP requests
- Add documentation for overriding HTCPCP templates
- Add changelog to Sphinx documentation
- Add API summary to Sphinx documentation
- Add support for the extension to the ``Safe`` header field from RFC 2324
- Amend minor typo in ``utils`` module docstrings
- Expand unit tests for ``views`` module
- Move ``require_htcpcp`` decorator to the ``decorators`` module
- Update the package installation instructions

v0.5.1
------

Released 2019-07-08

- Fix attribute error when running tests with Django 2.0 / Python 3.4

v0.5.0
------

Released 2019-07-08

- Add unit tests for the ``views`` module
- Add formal support for Python 3.7
- Expand ``utils`` unit tests
- Fix missing ``Alternates`` header due to generator exhaustion
- Fix ``Server`` header override when the WSGI implementation does not populate the ``SERVER_SOFTWARE`` variable
- Fix detection of supported teas in the request URI
- Refactor handling of ``Alternates`` header generation
- Refactor the pots data fixture to include a pot that supports a proper subset of available teas

v0.4.0
------

Released 2019-07-05

- Add setting to override the ``Server`` header for HTCPCP responses
- Add support for user-defined forbidden combinations of additions
- Add additional unit tests for the ``utils`` and ``models`` modules
- Add data fixture for demo forbidden combinations of additions
- Update README description
- Update package metadata
- Update reStructuredText formatting in the configuration docs
- Optimized model listings on the admin site

v0.3.1
------

Released 2019-06-25

- Remove Sphinx build directory from package data


v0.3.0
------

Released 2019-06-24

- Add Sphinx documentation for installation and configuration
- Add unit tests for the models module
- Update links in REAME.rst
- Fix typo in Travis-CI build matrix
- Fix error in ``utils`` module unit tests


v0.2.2
------

Released 2019-06-24

- Fix syntax error in Python 3.4
- Fix dependency errors for Travis-CI build jobs (123e022)


v0.2.1
------

Released 2019-06-24

- Add Travis-CI and Coveralls reporting to README

v0.2.0
------

Released 2019-06-24

- Add informative content to README
- Add data fixture for RFC 2324 additions
- Add data fixture for RFC 7168 additions
- Add data fixture for RFC 7168 teas
- Add data fixture for demo pots
- Add default ``coverage`` configuration
- Add Travis-CI integration
- Add script to run Django tests
- Add ``tests`` package
- Add unit tests for ``utils`` module
- Fix filter override in ``admin.PotsServingMixin``
- Fix duplicate tea types being recorded in admin counts
- Refactor template hierarchy
- Improve context visibility in templates
- Refactor logic for determining a pots addition and milk support

v0.1.2
------

Released 2019-06-23

- Re-release patch version due to packaging mishap

v0.1.1
------

Released 2019-06-23

- Add data files to package manifest

v0.1.0
------

Released 2019-06-21

- Add licence
- Add app class
- Add ``Pot`` model
- Add ``TeaType`` model
- Add ``Addition`` model
- Add initial admin site
- Add ``settings`` module
- Add initial url config
- Add initial HTCPCP middleware
- Add ``require_htcpcp`` decorator
- Add HTCPCP view
- Add initial templates
- Add ``utils`` module
- Add setup script
