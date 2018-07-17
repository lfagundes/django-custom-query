from django.test import TestCase
from customquery import Parser
from .models import TestModel
from django.db.models import Q

class ParserTest(TestCase):

    def setUp(self):
        self.parser = Parser(TestModel)

    def test_basic_number(self):
        qq = self.parser.parse("number=1")
        self.assertEquals(qq, Q(x=1))
        
        
        

