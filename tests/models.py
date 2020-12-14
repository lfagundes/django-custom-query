from django.db import models

class RelatedModel(models.Model):
    name = models.CharField(max_length=16)
    numfield = models.FloatField(null=True)
    numfield2 = models.FloatField(null=True)

class TestModel(models.Model):
    charfield = models.CharField(max_length=16)
    numfield = models.IntegerField(null=True)
    numfield2 = models.IntegerField(null=True)
    datefield = models.DateField()
    related = models.ForeignKey(RelatedModel, on_delete=models.CASCADE)
    first_name = models.CharField(max_length=16)
    last_name = models.CharField(max_length=16)
