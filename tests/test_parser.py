from django.test import TestCase
from customquery import Parser
from .models import TestModel
from django.db.models import Q

class ParserTest(TestCase):

    def setUp(self):
        self.parser = Parser(TestModel)

    def parse(self, query):
        return self.parser.parse(query)

    def test_number(self):
        self.assertEquals(self.parse("number=1"), Q(number=1))

    def test_whitespaces_are_ignored(self):
        self.assertEquals(self.parse("number = 1"), Q(number=1))
        self.assertEquals(self.parse("number  = 1"), Q(number=1))

    def test_basic_operators(self):
        self.assertEquals(self.parse("number > 1"), Q(number__gt=1))
        self.assertEquals(self.parse("number >= 1"), Q(number__gte=1))
        self.assertEquals(self.parse("number < 1"), Q(number__lt=1))
        self.assertEquals(self.parse("number <= 1"), Q(number__lte=1))

    def test_basic_operators(self):
        self.assertEquals(self.parse("number > 1"), Q(number__gt=1))
        self.assertEquals(self.parse("number >= 1"), Q(number__gte=1))
        self.assertEquals(self.parse("number < 1"), Q(number__lt=1))
        self.assertEquals(self.parse("number <= 1"), Q(number__lte=1))

    def test_not(self):
        self.assertEquals(self.parse("number <> 1"), ~Q(number=1))
        self.assertEquals(self.parse("number != 1"), ~Q(number=1))

    def test_single_string(self):
        self.assertEquals(self.parse('char=foo'), Q(char="foo"))
        self.assertEquals(self.parse('char="foo"'), Q(char="foo"))
        self.assertEquals(self.parse("char='foo'"), Q(char="foo"))
        
    def test_string_phrase(self):
        self.assertEquals(self.parse('char="foo bar"'), Q(char="foo bar"))
        self.assertEquals(self.parse("char='foo bar'"), Q(char="foo bar"))
        
        
        

