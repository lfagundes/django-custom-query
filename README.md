django-custom-query
=====


[![Test customquery](https://github.com/ivan-katkov/django-custom-query/actions/workflows/tests.yml/badge.svg)](https://github.com/ivan-katkov/django-custom-query/actions/workflows/tests.yml)

**django-custom-query** is a python module to write user provided search queries, using AND, OR and parenthesis grouping. This module will translate those to Django ORM Q objects.

Documentation is available at https://django-custom-query.readthedocs.io/ or else, you can build it from source like this::

    $ easy_install Sphinx
    $ cd docs
    $ make html

then open _build/html/index.html in your web browser.

To run tests:

    $ python3 run_tests.py
