from django.db import models

class TestModel(models.Model):
    charfield = models.CharField(max_length=16)
    numfield = models.IntegerField()
    datefield = models.DateField()
