from django.test import TestCase
from customquery import Parser
from .models import TestModel
from django.db.models import Q

class BaseTest(TestCase):
    def setUp(self):
        self.parser = Parser(TestModel)

    def parse(self, query):
        return self.parser.parse(query)

class SingleParserTest(BaseTest):

    def test_number(self):
        self.assertEquals(self.parse("numfield=1"), Q(numfield=1))

    def test_whitespaces_are_ignored(self):
        self.assertEquals(self.parse("numfield = 1"), Q(numfield=1))
        self.assertEquals(self.parse("numfield  = 1"), Q(numfield=1))

    def test_basic_operators(self):
        self.assertEquals(self.parse("numfield > 1"), Q(numfield__gt=1))
        self.assertEquals(self.parse("numfield >= 1"), Q(numfield__gte=1))
        self.assertEquals(self.parse("numfield < 1"), Q(numfield__lt=1))
        self.assertEquals(self.parse("numfield <= 1"), Q(numfield__lte=1))

    def test_basic_operators(self):
        self.assertEquals(self.parse("numfield > 1"), Q(numfield__gt=1))
        self.assertEquals(self.parse("numfield >= 1"), Q(numfield__gte=1))
        self.assertEquals(self.parse("numfield < 1"), Q(numfield__lt=1))
        self.assertEquals(self.parse("numfield <= 1"), Q(numfield__lte=1))

    def test_not(self):
        self.assertEquals(self.parse("numfield <> 1"), ~Q(numfield=1))
        self.assertEquals(self.parse("numfield != 1"), ~Q(numfield=1))

    def test_single_string(self):
        self.assertEquals(self.parse('charfield=foo'), Q(charfield="foo"))
        self.assertEquals(self.parse('charfield="foo"'), Q(charfield="foo"))
        self.assertEquals(self.parse("charfield='foo'"), Q(charfield="foo"))
        
    def test_string_phrase(self):
        self.assertEquals(self.parse('charfield="foo bar"'), Q(charfield="foo bar"))
        self.assertEquals(self.parse("charfield='foo bar'"), Q(charfield="foo bar"))

