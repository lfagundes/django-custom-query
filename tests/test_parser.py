from datetime import datetime, date
from django.test import TestCase, tag
from customquery import Parser, exceptions
from .models import MainModel
from django.db.models import Q, F, Value as V
from django.db.models.functions import Concat


class BaseTest(TestCase):
    def setUp(self):
        self.parser = Parser(MainModel)

    def parse(self, query):
        return self.parser.parse(query)


class SingleParserTest(BaseTest):

    def test_number(self):
        self.assertEqual(self.parse("numfield=1"), Q(numfield=1))

    def test_number_float(self):
        self.assertEqual(self.parse("numfield=1.1"), Q(numfield=1.1))

    def test_whitespaces_are_ignored(self):
        self.assertEqual(self.parse("numfield = 1"), Q(numfield=1))
        self.assertEqual(self.parse("numfield  = 1"), Q(numfield=1))

    def test_basic_operators(self):
        self.assertEqual(self.parse("numfield > 1"), Q(numfield__gt=1))
        self.assertEqual(self.parse("numfield >= 1"), Q(numfield__gte=1))
        self.assertEqual(self.parse("numfield < 1"), Q(numfield__lt=1))
        self.assertEqual(self.parse("numfield <= 1"), Q(numfield__lte=1))

    def test_tilda_operator_number(self):
        self.assertEqual(self.parse("numfield ~ 0.1"),
                          Q(numfield__icontains=0.1))
        self.assertEqual(self.parse("numfield ~ -0.1"),
                          Q(numfield__icontains=-0.1))

    def test_not(self):
        self.assertEqual(self.parse("numfield <> 1"), ~Q(numfield=1))
        self.assertEqual(self.parse("numfield != 1"), ~Q(numfield=1))

    def test_not_as_keyword(self):
        self.assertEqual(self.parse("numfield NOT 1"), ~Q(numfield=1))

    def test_in_operator_with_numerical_field(self):
        self.assertEqual(self.parse("numfield IN (1, 2, 3, 4)"),
                          Q(numfield__in=(1, 2, 3, 4)))

    def test_in_operator_with_numerical_field_lower_case(self):
        self.assertEqual(self.parse("numfield in (1, 2, 3, 4)"),
                          Q(numfield__in=(1, 2, 3, 4)))

    def test_not_in_operator(self):
        self.assertEqual(self.parse("numfield NOT IN (1, 2, 3, 4)"), ~Q(
            numfield__in=(1, 2, 3, 4)))

    def test_not_in_operator_lower_case(self):
        self.assertEqual(self.parse("numfield not in (1, 2, 3, 4)"), ~Q(
            numfield__in=(1, 2, 3, 4)))

    def test_not_in_operator_mix_case1(self):
        self.assertEqual(self.parse("numfield not IN (1, 2, 3, 4)"), ~Q(
            numfield__in=(1, 2, 3, 4)))

    def test_not_in_operator_mix_case2(self):
        self.assertEqual(self.parse("numfield NOT in (1, 2, 3, 4)"), ~Q(
            numfield__in=(1, 2, 3, 4)))

    def test_not_in_operator_mix_case2(self):
        self.assertEqual(self.parse("numfield Not iN (1, 2, 3, 4)"), ~Q(
            numfield__in=(1, 2, 3, 4)))

    def test_in_operator_with_string_field(self):
        self.assertEqual(self.parse("charfield IN ('one', 'two', 'three')"), Q(
            charfield__in=('one', 'two', 'three')))
        self.assertEqual(self.parse('charfield IN ("one", "two", "three")'), Q(
            charfield__in=('one', 'two', 'three')))

    def test_single_string(self):
        self.assertEqual(self.parse('charfield=foo'), Q(charfield="foo"))
        self.assertEqual(self.parse('charfield="foo"'), Q(charfield="foo"))
        self.assertEqual(self.parse("charfield='foo'"), Q(charfield="foo"))

    def test_string_phrase(self):
        self.assertEqual(self.parse('charfield="foo bar"'),
                          Q(charfield="foo bar"))
        self.assertEqual(self.parse("charfield='foo bar'"),
                          Q(charfield="foo bar"))

    def test_string_tilda_operator(self):
        self.assertEqual(self.parse('charfield~"foo"'),
                          Q(charfield__icontains="foo"))
        self.assertEqual(self.parse('charfield~"foo bar"'),
                          Q(charfield__icontains="foo bar"))

    def test_is_null(self):
        self.assertEqual(self.parse('numfield IS NULL'),
                          Q(numfield__isnull=True))

    def test_is_not_null(self):
        self.assertEqual(self.parse('numfield IS NOT NULL'),
                          Q(numfield__isnull=False))


class RelatedModelTest(BaseTest):
    def test_related_field(self):
        self.assertEqual(self.parse('related__name="foo bar"'),
                          Q(related__name="foo bar"))

    def test_related_field_can_be_acessed_with_dot(self):
        self.assertEqual(self.parse('related.name="foo bar"'),
                          Q(related__name="foo bar"))

    def test_related_field_mathexpression(self):
        self.assertEqual(self.parse('related__numfield + numfield > 1'),
                          Q(related__numfield__gt=1 - F('numfield')))

    def test_related_field_mathexpression2(self):
        self.assertEqual(self.parse('numfield / related__numfield = -3.14'),
                          Q(numfield=-3.14 * F('related__numfield')))

    def test_related_field_mathexpression_dot_sum(self):
        self.assertEqual(self.parse('related.numfield + numfield > 1'),
                          Q(related__numfield__gt=1 - F('numfield')))

    def test_related_field_mathexpression_dot_mul(self):
        self.assertEqual(self.parse('related.numfield * numfield >= 2.0'),
                          Q(related__numfield__gte=2.0 / F('numfield')))

    def test_related_field_mathexpression_dot_div(self):
        self.assertEqual(self.parse('numfield / related.numfield = -3.14'),
                          Q(numfield=-3.14 * F('related__numfield')))

    def test_related_field_mathexpression_dot_sub(self):
        self.assertEqual(self.parse('numfield + related.numfield <= 2'),
                          Q(numfield__lte=2 - F('related__numfield')))

    def test_related_field_mathexpression_dot_sum_two_related_fields(self):
        self.assertEqual(self.parse('related.numfield + related.numfield2 > 3'),
                          Q(related__numfield__gt=3 - F('related__numfield2')))

    def test_related_field_mathexpression_dot_sum_two_related_fields(self):
        self.assertEqual(self.parse('related.numfield / related.numfield2 = 1'),
                          Q(related__numfield=1 * F('related__numfield2')))

class AnnotationTest(BaseTest):
    def setUp(self):
        qs = MainModel.objects.annotate(
            full_name=Concat('first_name', V(' '), 'last_name'))
        self.parser = Parser(qs)

    def test_annotated_field(self):
        self.assertEqual(self.parse('full_name="foo bar"'),
                          Q(full_name="foo bar"))


class SimpleOperatorTest(BaseTest):

    def test_or(self):
        self.assertEqual(self.parse('numfield=1 or charfield="foo"'),
                          Q(numfield=1) | Q(charfield="foo"))
        self.assertEqual(self.parse('numfield=1 OR charfield="foo"'),
                          Q(numfield=1) | Q(charfield="foo"))
        self.assertEqual(self.parse('numfield = 1 or charfield="foo"'),
                          Q(numfield=1) | Q(charfield="foo"))
        self.assertEqual(self.parse("numfield=1 OR charfield = 'foo'"),
                          Q(numfield=1) | Q(charfield="foo"))

    def test_and(self):
        self.assertEqual(self.parse('numfield=1 and charfield="foo"'),
                          Q(numfield=1) & Q(charfield="foo"))
        self.assertEqual(self.parse('numfield=1 AND charfield="foo"'),
                          Q(numfield=1) & Q(charfield="foo"))


class MathOperatorTest(BaseTest):

    # def test_test(self):
    #     print(F('numfield') + F('numfield2'))

    def test_plus_gt(self):
        self.assertEqual(self.parse('numfield + numfield2 > 1'),
                          Q(numfield__gt=1-F('numfield2')))

    def test_plus_gte(self):
        self.assertEqual(self.parse('numfield + numfield2 >= 2.0'),
                          Q(numfield__gte=2.0-F('numfield2')))

    def test_plus_lt(self):
        self.assertEqual(self.parse('numfield + numfield2 < -2'),
                          Q(numfield__lt=-2-F('numfield2')))

    def test_plus_lte(self):
        self.assertEqual(self.parse('numfield + numfield2 <= -4.5'),
                          Q(numfield__lte=-4.5-F('numfield2')))

    def test_plus_eq(self):
        self.assertEqual(self.parse('numfield + numfield2 = 1'),
                          Q(numfield=1-F('numfield2')))

    def test_plus_noteq(self):
        self.assertEqual(self.parse('numfield + numfield2 != 1'),
                          ~Q(numfield=1-F('numfield2')))

    def test_plus_not(self):
        self.assertEqual(self.parse('numfield + numfield2 NOT 1'),
                          ~Q(numfield=1-F('numfield2')))

    def test_plus_tilda(self):
        self.assertEqual(self.parse('numfield + numfield2 ~ 1'),
                          Q(numfield__icontains=1-F('numfield2')))

    def test_minus(self):
        self.assertEqual(self.parse('numfield - numfield2 > 1'),
                          Q(numfield__gt=1+F('numfield2')))

    def test_multiplication_gt(self):
        self.assertEqual(self.parse('numfield * numfield2 > 1'),
                          Q(numfield__gt=1 / F('numfield2')))

    def test_multiplication_gte(self):
        self.assertEqual(self.parse('numfield * numfield2 >= 2.0'),
                          Q(numfield__gte=2.0 / F('numfield2')))

    def test_multiplication_lt(self):
        self.assertEqual(self.parse('numfield * numfield2 < -3'),
                          Q(numfield__lt=-3 / F('numfield2')))

    def test_multiplication_lte(self):
        self.assertEqual(self.parse('numfield * numfield2 <= -6.7'),
                          Q(numfield__lte=-6.7 / F('numfield2')))

    def test_division(self):
        self.assertEqual(self.parse('numfield / numfield2 > 1'),
                          Q(numfield__gt=1 * F('numfield2')))


class ParenthesisTest(BaseTest):

    def test_one_parenthesis(self):
        self.assertEqual(self.parse('numfield=1 or (numfield > 5 and numfield < 10)'),
                          Q(numfield=1) | (Q(numfield__gt=5) & Q(numfield__lt=10)))

    def test_one_parenthesis_mathexpression(self):
        self.assertEqual(self.parse('numfield=1 or (numfield > 5 and numfield - numfield2 < 10)'),
                          Q(numfield=1) | (Q(numfield__gt=5) & Q(numfield__lt=10+F('numfield2'))))

    def test_complex_parenthesis(self):
        query = ('numfield=1 or ' +
                 '(numfield > 5 and (numfield <= 10 or charfield = "foobar"))')
        expected = Q(numfield=1) | (Q(numfield__gt=5) & (
            Q(numfield__lte=10) | Q(charfield="foobar")))

        self.assertEqual(self.parse(query), expected)


class BetweenTest(BaseTest):

    def test_between_number(self):
        self.assertEqual(self.parse('numfield between 1 and 5'),
                         Q(numfield__gte=1) & Q(numfield__lte=5))

    def test_between_number_uppercase(self):
        self.assertEqual(self.parse('numfield BETWEEN 1 AND 5'),
                         Q(numfield__gte=1) & Q(numfield__lte=5))    

    def test_between_number_mathexpression(self):
        self.assertEqual(self.parse('numfield - numfield2 between 1 and 5'),
                         Q(numfield__gte=1+F('numfield2')) & Q(numfield__lte=5+F('numfield2')))

    def test_between_char(self):
        self.assertEqual(self.parse('charfield between "foo" and "foo bar"'),
                         Q(charfield__gte="foo") & Q(charfield__lte="foo bar"))

    def test_between_number_mathexpression_complex(self):
        self.assertEqual(
            self.parse('numfield - numfield2 between 1 and 5 and numfield2 < 3'),
            (Q(numfield__gte=1+F('numfield2')) & Q(numfield__lte=5+F('numfield2'))) & Q(numfield2__lt=3)
            )

    def test_between_number_mathexpression_complex_surrounded_logical_operators(self):
        self.assertEqual(
            self.parse('numfield = 9 OR numfield - numfield2 between 1 and 5 and numfield2 < 3'),
            Q(numfield=9) | (Q(numfield__gte=1+F('numfield2')) & Q(numfield__lte=5+F('numfield2'))) & Q(numfield2__lt=3)
            )

class ValidationTest(BaseTest):

    def test_field_must_exist_in_model(self):
        # Use field that is not present on MainModel
        try:
            self.parse("unknown > 10")
        except exceptions.FieldDoesNotExist as e:
            self.assertEqual(e.field, 'unknown')
        else:
            self.fail("Unknown field shouldn't be accepted")

    def test_parenthesis_must_match(self):
        try:
            self.parse("(numfield > 10")
        except exceptions.ParenthesisDontMatch:
            pass
        else:
            self.fail("Parenthesis matching is not properly validated")

    def test_check_unknown_operator(self):
        try:
            parsed = self.parse("numfield ? 10")
            import ipdb
            ipdb.set_trace()
        except exceptions.UnknownOperator as e:
            self.assertEqual(e.operator, "?")
        else:
            self.fail("Operator should be checked")


class DateFormatTest(TestCase):

    def test_date_without_format(self):
        parser = Parser(MainModel)
        self.assertEqual(parser.parse('datefield="2018-12-13"'),
                          Q(datefield=date(2018, 12, 13)))

    def test_date_with_format(self):
        parser = Parser(MainModel, date_format='%d/%m/%Y')
        self.assertEqual(parser.parse('datefield="13/12/2018"'),
                          Q(datefield=date(2018, 12, 13)))
        self.assertEqual(parser.parse('datefield=13/12/2018'),
                          Q(datefield=date(2018, 12, 13)))


class MultipleLogicalOperatorsTest(BaseTest):

    def test_two_and(self):
        self.assertEqual(
            self.parse('numfield=1 and numfield > 5 and numfield < 10'),
            Q(numfield=1) & Q(numfield__gt=5) & Q(numfield__lt=10)
            )

    def test_two_and_or(self):
        self.assertEqual(
            self.parse('numfield=1 or numfield > 5 and numfield < 10'),
            Q(numfield=1) | Q(numfield__gt=5) & Q(numfield__lt=10)
            )

    def test_three_and_or(self):
        self.assertEqual(
            self.parse('numfield=1 or numfield > 5 and numfield < 10 and numfield2 != 4'),
            Q(numfield=1) | Q(numfield__gt=5) & Q(numfield__lt=10) & ~Q(numfield2=4))

    def test_four_and_or(self):
        self.assertEqual(
            self.parse('numfield>-0.3 and numfield < 1 or numfield2 != 10 and numfield2 > 14'),
            Q(numfield__gt=-0.3) & Q(numfield__lt=1) | ~Q(numfield2=10) & Q(numfield2__gt=14))


class LogicalOperatorsParenthesisTest(BaseTest):

    def test1(self):
        self.assertEqual(
            self.parse('(numfield=1 or numfield > 5) and numfield < 10'),
            (Q(numfield=1) | Q(numfield__gt=5)) & Q(numfield__lt=10)
            )

    def test2(self):
        self.assertEqual(
            self.parse('numfield=1 and (numfield > 5 or numfield < 10)'),
            Q(numfield=1) & (Q(numfield__gt=5) | Q(numfield__lt=10))
            )


class ConeSearchTest(BaseTest):

    def test_basic1(self):
        self.assertEqual(self.parse('cone(120.3, 23, 1.0)'), Q(cone_query=True))

        self.assertTrue(hasattr(self.parser, 'extra_params'))
        self.assertEqual(len(self.parser.extra_params['cones']), 1)

        self.assertEqual(self.parser.extra_params['cones'][0]['cone_ra'], 120.3)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_dec'], 23.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_radius'], 1.0)

        # reset Cone status parameters
        self.parser.extra_params['cones'] = []

    def test_basic2(self):
        self.assertEqual(self.parse('cone(10, -13, 2)'), Q(cone_query=True))

        self.assertTrue(hasattr(self.parser, 'extra_params'))
        self.assertEqual(len(self.parser.extra_params['cones']), 1)

        self.assertEqual(self.parser.extra_params['cones'][0]['cone_ra'], 10.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_dec'], -13.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_radius'], 2.0)

        self.parser.extra_params['cones'] = []

    def test_basic3(self):
        self.assertEqual(self.parse('cone(102, -56, 1.2)'), Q(cone_query=True))

        self.assertEqual(self.parser.extra_params['cones'][0]['cone_ra'], 102.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_dec'], -56.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_radius'], 1.2)

        self.parser.extra_params['cones'] = []

    def test_complex1(self):
        self.assertEqual(
            self.parse('numfield>1 and cone(102, -56, 1.2)'),
            Q(numfield__gt=1) & Q(cone_query=True))
        

        self.assertEqual(self.parser.extra_params['cones'][0]['cone_ra'], 102.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_dec'], -56.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_radius'], 1.2)

        self.parser.extra_params['cones'] = []

    def test_complex2(self):
        self.assertEqual(
            self.parse('cone(102, -56, 1.2) OR numfield - numfield2 between 1 and 5'),
            Q(cone_query=True) | (Q(numfield__gte=1+F('numfield2')) & Q(numfield__lte=5+F('numfield2')))
            )

        self.assertTrue(hasattr(self.parser, 'extra_params'))
        self.assertEqual(len(self.parser.extra_params['cones']), 1)

        self.assertEqual(self.parser.extra_params['cones'][0]['cone_ra'], 102.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_dec'], -56.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_radius'], 1.2)
        self.parser.extra_params['cones'] = []

    def test_wrong_cone_arguments(self):
        with self.assertRaises(exceptions.InvalidConeArguments):
            self.parse('cone(120.3, 23, 1.0, 12.3)')

    def test_two_cones(self):
        self.assertEqual(
            self.parse('cone(120.3, 23, 1.0) or cone(10.3, -23, 1.5)'),
            Q(cone_query=True) | Q(cone_query1=True))

        self.assertTrue(hasattr(self.parser, 'extra_params'))
        self.assertEqual(len(self.parser.extra_params['cones']), 2)

        self.assertEqual(self.parser.extra_params['cones'][0]['cone_ra'], 120.3)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_dec'], 23.0)
        self.assertEqual(self.parser.extra_params['cones'][0]['cone_radius'], 1.0)

        self.assertEqual(self.parser.extra_params['cones'][1]['cone_ra'], 10.3)
        self.assertEqual(self.parser.extra_params['cones'][1]['cone_dec'], -23.0)
        self.assertEqual(self.parser.extra_params['cones'][1]['cone_radius'], 1.5)
