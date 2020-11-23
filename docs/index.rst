===================
Django Custom Query
===================

django-custom-query is a python module to write user provided search queries, using AND, OR and parenthesis grouping. This module will translate those to Django ORM Q objects.

Install
=======

    $ pip3 install django-custom-query

django-custom-query was developed and tested on Python 3.5. Is based on `sqlparse`_.

.. _sqlparse: https://github.com/andialbrecht/sqlparse

Source
======

Source can be downloaded as a tar.gz file from http://pypi.python.org/pypi/django-custom-query

Using `git <http://git-scm.com/>`_ you can clone the source from http://github.com/lfagundes/django-custom-query.git

django-custom-query is free and open for usage under the `MIT license`_.

.. _MIT license: http://en.wikipedia.org/wiki/MIT_License



Documentation
=============

Contents:

.. toctree::
   :maxdepth: 2

   using

.. _api:

API Reference
=============

.. toctree::
    :glob:
    
    api/django-custom-query

Contributing
============

Please submit `bugs and patches <http://github.org/lfagundes/django-custom-query/issues/>`_, preferably with tests.  All contributors will be acknowledged.  Thanks!

Credits
=======

django-custom-query was created by Luis Fagundes and was sponsored by `Spatial Datalyst <http://spatialdatalyst.com/>`_.

Changelog
=========

- 0.4.1

  - Support for LIKE operator
 
- 0.4.0

  - Support for IS NULL and IS NOT NULL queries
    
- 0.3.0

  - Support for annotations
  - Support for date formatting
  - NOT operator
  - IN operator

- 0.2.0

  - Support for filters on models.ForeignKey fields

- 0.1.0

  - Initial release, with support for integer and char fields, =, >, <, <=, <=, <>, !=, AND, OR, BETWEEN and parenthesis.

