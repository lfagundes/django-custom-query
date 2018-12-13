
.. _using:

=========================
Using Django Custom Query
=========================

    >>> from customquery import Parser
    >>> from myapp import MyModel
    >>>
    >>> parser = Parser(MyModel)
    >>> query = parser.parse("numberfield = 10 or (numberfield > 20 and numberfield < 30)")
    >>> items = MyModel.objects.filter(query)

Parser.parse() will create Django Q objects based on SQL-like condition statements.

The model is used for field validation and proper interpretation of field input:

    >>> class MyModel(models.Model):
    >>>     numberfield = models.IntegerField()

Foreign Keys
============

    >>> class RelatedModel(models.Model):
    >>>     name = models.CharField(max_length=16)
    >>>
    >>> class MyModel(models.Model):
    >>>     related = models.ForeignKey(RelatedModel, on_delete=models.CASCADE)
    >>>
    >>> parser = Parser(MyModel)
    >>> query = parser.parse('related__name="foo bar"')
    >>> query = parser.parse('related.name="foo bar"') # dots can be used instead of __

Annotations
===========

    >>> from django.db.models import Value
    >>> from django.db.models.functions import Concat
    >>>
    >>> qs = MyModel.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name')).all()
    >>> parser = Parser(qs)
    >>> query = parser.parse('full_name="foo bar"')

Date formatting
===============
    >>> class MyModel(models.Model):
    >>>     birthday = models.DateField()
    >>>
    >>> parser = Parser(MyModel, date_format='%d/%m/%Y')
    >>> parser.parse('birthday=13/12/2018')

Operators
=========

    >>> parser.parse("numfield=1")     # Q(numfield=1))
    >>> parser.parse("numfield = 1")   # Q(numfield=1))
    >>> parser.parse("numfield  = 1")  # Q(numfield=1))
    >>> parser.parse("numfield > 1")   # Q(numfield__gt=1))
    >>> parser.parse("numfield >= 1")  # Q(numfield__gte=1))
    >>> parser.parse("numfield < 1")   # Q(numfield__lt=1))
    >>> parser.parse("numfield <= 1")  # Q(numfield__lte=1))
    >>> parser.parse("numfield > 1")   # Q(numfield__gt=1))
    >>> parser.parse("numfield >= 1")  # Q(numfield__gte=1))
    >>> parser.parse("numfield < 1")   # Q(numfield__lt=1))
    >>> parser.parse("numfield <= 1")  # Q(numfield__lte=1))
    >>> parser.parse("numfield <> 1")  # ~Q(numfield=1))
    >>> parser.parse("numfield != 1")  # ~Q(numfield=1))
    >>> parser.parse("numfield NOT 1") # ~Q(numfield=1))
