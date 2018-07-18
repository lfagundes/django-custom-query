
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
    





