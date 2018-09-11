from django.db import models

class RelatedModel(models.Model):
    name = models.CharField(max_length=16)

class TestModel(models.Model):
    charfield = models.CharField(max_length=16)
    numfield = models.IntegerField()
    datefield = models.DateField()
    related = models.ForeignKey(RelatedModel, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
