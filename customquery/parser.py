import sqlparse
from django.db.models import Q

class Parser:

    def __init__(self, model):
        self.model = model

    def parse(self, query):
        return Q(x=1)
