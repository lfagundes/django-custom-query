
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

The model is used for field validation:

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
    





