from django.db import models

class TestModel(models.Model):
    char = models.CharField(max_length=16)
    number = models.IntegerField()
    date = models.DateField()
