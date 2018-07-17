from sqlparse import parse, tokens as t, sql
from django.db.models import Q

class Parser:

    def __init__(self, model):
        self.model = model

    def parse(self, query):
        result = Q()
        parsed = parse(query)[0]
        tokens = self._remove_whitespaces(parsed.tokens[0])
        return self.compare(tokens)

    def compare(self, tokens):
        assert len(tokens) == 3
        (identifier, comparison, value) = tokens

        key = identifier.value
        key, cond = self.make_key(comparison, key)
        kwargs = {}
        
        if value.ttype is t.Token.Literal.Number.Integer:
            kwargs[key] = int(value.value)
        elif isinstance(value, sql.Identifier):
            kwargs[key] = value.get_name()
        elif value.ttype is t.Token.Literal.String.Single:
            v = value.value
            if v.startswith("'") and v.endswith("'"):
                v = v[1:-1]
            kwargs[key] = v

        result = Q(**kwargs)
        if not cond:
            result = ~result
        return result

    def make_key(self, op, key):
        comp = t.Token.Operator.Comparison
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
        return [key, True]

    def _remove_whitespaces(self, tokens):
        return [ tok for tok in tokens if not tok.ttype is t.Token.Text.Whitespace ]
