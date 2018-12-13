from sqlparse import parse, tokens as t, sql
from datetime import datetime, date
from django.core import exceptions as django_exceptions
from . import exceptions
from django.db.models import fields, Q, QuerySet

class Parser:

    def __init__(self, model, date_format='%Y-%m-%d'):
        self.model = model
        self.date_format = date_format

    def parse(self, query):
        """Parse SQL-like condition statements and return Django Q objects"""

        result = Q()
        parsed = parse(query)[0]
        return self._resolve(parsed.tokens)

    def _resolve(self, tokens):
        tokens = self._strip_whitespaces(tokens)
        if len(tokens) == 1:
            return self._resolve(tokens[0])
        if tokens[0].match(t.Token.Punctuation, '('):
            tokens = self._get_group(tokens)
        operator = tokens[1]
        if operator.ttype is t.Token.Keyword:
            if operator.match(t.Token.Keyword, 'BETWEEN'):
                assert(len(tokens) == 5)
                return self._between(tokens[0], tokens[2], tokens[4])
            elif operator.match(t.Token.Keyword, 'NOT'):
                if len(tokens) == 3:
                    return self._compare(*tokens)
                if len(tokens) == 4 and tokens[2].match(t.Token.Keyword, 'IN'):
                    return ~self._in(tokens[0], tokens[3])
                raise exceptions.InvalidQuery()
            if operator.match(t.Token.Keyword, 'IN'):
                return self._in(tokens[0], tokens[2])
            else:
                a = self._resolve(tokens[0])
                b = self._resolve(tokens[2])
                return self._operate(a, tokens[1], b)
        else:
            if len(tokens) > 3:
                #import ipdb; ipdb.set_trace()
                raise Exception("Invalid query")
            return self._compare(*tokens)

    def _between(self, subject, floor, ceil):
        gte = parse('a>=1')[0].tokens[0].tokens[1]
        lte = parse('a<=1')[0].tokens[0].tokens[1]
        first = self._resolve([subject, gte, floor])
        second = self._resolve([subject, lte, ceil])
        return first & second

    def _in(self, subject, values):
        tokens = values.tokens
        if tokens[0].value == '(':
            tokens = self._get_group(tokens)
        else:
            raise exceptions.ParenthesisExpected('IN')

        if not len(tokens) == 1:
            raise exceptions.MalformedList

        kwargs = {
            '%s__in' % subject.value: self._get_list(subject.value, tokens[0].tokens),
        }

        return Q(**kwargs)

    def _operate(self, a, operator, b):
        if operator.match(t.Token.Keyword, 'OR'):
            return a | b
        if operator.match(t.Token.Keyword, 'AND'):
            return a & b

    def _compare(self, subject, operator, predicate):
        # Raise exception if field does not exist
        key, cond = self._make_key(operator, subject.value)
        kwargs = {}
        kwargs[key] = self._get_value(subject.value, predicate)

        result = Q(**kwargs)
        if not cond:
            result = ~result
        return result

    def _get_list(self, key, tokens):
        tokens = self._strip_whitespaces(tokens)
        objects = []
        while len(tokens) > 0:
            next_object = tokens.pop(0)
            objects.append(self._get_value(key, next_object))
            if len(tokens) > 0:
                punctuation = tokens.pop(0)
                if not punctuation.ttype is t.Token.Punctuation or not punctuation.value == ',':
                    raise exceptions.MalformedList()
        return tuple(objects)

    def _get_value(self, key, predicate):
        v = predicate.value
        if v.startswith("'") and v.endswith("'"):
            v = v[1:-1]
        elif v.startswith('"') and v.endswith('"'):
            v = v[1:-1]

        field = self._get_field(key)
        if isinstance(field, fields.DateField):
            return datetime.strptime(str(v), self.date_format).date()
        if predicate.ttype is t.Token.Literal.Number.Integer:
            return int(v)
        if isinstance(predicate, sql.Identifier):
            return predicate.get_name()
        if predicate.ttype is t.Token.Literal.String.Single:
            return v

    def _make_key(self, op, key):
        comp = t.Token.Operator.Comparison
        key = key.replace('.', '__')
        if op.match(comp, '='):
            return [key, True]
        if op.match(comp, '>'):
            return [key + '__gt', True]
        if op.match(comp, '>='):
            return [key + '__gte', True]
        if op.match(comp, '<'):
            return [key + '__lt', True]
        if op.match(comp, '<='):
            return [key + '__lte', True]
        if op.match(comp, '<>'):
            return [key, False]
        if op.match(comp, '!='):
            return [key, False]
        if op.value == 'NOT':
            return [key, False]
        raise exceptions.UnknownOperator(op.normalized)

    def _get_field(self, key):
        model = self.model

        if isinstance(model, QuerySet):
            qs = model
            if qs.query.annotations.get(key):
                return None
            model = qs.model

        key = key.replace('.', '__')
        path = key.split('__')
        while len(path) > 1:
            model = model._meta.get_field(path.pop(0)).related_model
        try:
            return model._meta.get_field(path[0])
        except django_exceptions.FieldDoesNotExist:
            raise exceptions.FieldDoesNotExist(key)

    def _get_group(self, tokens):
        if tokens[-1].match(t.Token.Punctuation, ')'):
            return tokens[1:-1]
        else:
            raise exceptions.ParenthesisDontMatch()

    def _strip_whitespaces(self, tokens):
        return [ tok for tok in tokens if not tok.ttype is t.Token.Text.Whitespace ]
