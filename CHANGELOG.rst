Changes
=======

For complete record of changes, see the commit log of the `public git repository`_.

.. _public git repository: https://github.com/blueschu/django-htcpcp-tea

v0.4.0
------

Released ???

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
