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
        tokens = [ tok for tok in tokens if not tok.ttype is t.Token.Text.Whitespace ]
        if len(tokens) == 1:
            return self._resolve(tokens[0])
        if tokens[0].match(t.Token.Punctuation, '('):
            if tokens[-1].match(t.Token.Punctuation, ')'):
                tokens = tokens[1:-1]
            else:
                raise exceptions.ParenthesisDontMatch()
        operator = tokens[1]
        if operator.ttype is t.Token.Keyword:
            if operator.match(t.Token.Keyword, 'BETWEEN'):
                assert(len(tokens) == 5)
                return self._between(tokens[0], tokens[2], tokens[4])
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

    def _operate(self, a, operator, b):
        if operator.match(t.Token.Keyword, 'OR'):
            return a | b
        if operator.match(t.Token.Keyword, 'AND'):
            return a & b

    def _compare(self, subject, operator, predicate):
        key = subject.value
        # Raise exception if field does not exist
        field = self._get_field(self.model, key)
        key, cond = self._make_key(operator, key)
        kwargs = {}

        v = predicate.value
        if v.startswith("'") and v.endswith("'"):
            v = v[1:-1]
        elif v.startswith('"') and v.endswith('"'):
            v = v[1:-1]

        if isinstance(field, fields.DateField):
            kwargs[key] = datetime.strptime(str(v), self.date_format).date()
        elif predicate.ttype is t.Token.Literal.Number.Integer:
            kwargs[key] = int(v)
        elif isinstance(predicate, sql.Identifier):
            kwargs[key] = predicate.get_name()
        elif predicate.ttype is t.Token.Literal.String.Single:
            kwargs[key] = v

        result = Q(**kwargs)
        if not cond:
            result = ~result
        return result

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
        raise exceptions.UnknownOperator(op.normalized)

    def _get_field(self, model, key):
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
