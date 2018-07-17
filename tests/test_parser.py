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

class SimpleOperatorTest(BaseTest):

    def test_or(self):
        self.assertEquals(self.parse('numfield=1 or charfield="foo"'),
                          Q(numfield=1) | Q(charfield="foo"))
        self.assertEquals(self.parse('numfield=1 OR charfield="foo"'),
                          Q(numfield=1) | Q(charfield="foo"))
        self.assertEquals(self.parse('numfield = 1 or charfield="foo"'),
                          Q(numfield=1) | Q(charfield="foo"))
        self.assertEquals(self.parse("numfield=1 OR charfield = 'foo'"),
                          Q(numfield=1) | Q(charfield="foo"))
    def test_and(self):
        self.assertEquals(self.parse('numfield=1 and charfield="foo"'),
                          Q(numfield=1) & Q(charfield="foo"))
        self.assertEquals(self.parse('numfield=1 AND charfield="foo"'),
                          Q(numfield=1) & Q(charfield="foo"))

class ParenthesisTest(BaseTest):

    def test_one_parenthesis(self):
        self.assertEquals(self.parse('numfield=1 or (numfield > 5 and numfield < 10)'),
                          Q(numfield=1) | (Q(numfield__gt=5) & Q(numfield__lt=10)))
        
    def test_complex_parenthesis(self):
        query = ('numfield=1 or ' +
                 '(numfield > 5 and (numfield <= 10 or charfield = "foobar"))')
        expected = Q(numfield=1) | (Q(numfield__gt=5) & (Q(numfield__lte=10) | Q(charfield="foobar")))

        self.assertEquals(self.parse(query), expected)
        
