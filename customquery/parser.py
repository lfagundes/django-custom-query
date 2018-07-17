from sqlparse import parse, tokens as t, sql
from django.db.models import Q

class Parser:

    def __init__(self, model):
        self.model = model

    def parse(self, query):
        result = Q()
        parsed = parse(query)[0]
        return self.resolve(parsed.tokens)

    def resolve(self, tokens):
        tokens = [ tok for tok in tokens if not tok.ttype is t.Token.Text.Whitespace ]
        if len(tokens) == 1:
            return self.resolve(tokens[0])
        if tokens[0].match(t.Token.Punctuation, '(') and tokens[-1].match(t.Token.Punctuation, ')'):
            tokens = tokens[1:-1]
        operator = tokens[1]
        if operator.ttype is t.Token.Keyword:
            if operator.match(t.Token.Keyword, 'BETWEEN'):
                assert(len(tokens) == 5)
                return self.between(tokens[0], tokens[2], tokens[4])
            else:
                a = self.resolve(tokens[0])
                b = self.resolve(tokens[2])
                return self.operate(a, tokens[1], b)
        else:
                    
            if len(tokens) > 3:
                import ipdb; ipdb.set_trace()
            return self.compare(*tokens)

    def between(self, subject, floor, ceil):
        gte = parse('a>=1')[0].tokens[0].tokens[1]
        lte = parse('a<=1')[0].tokens[0].tokens[1]
        first = self.resolve([subject, gte, floor])
        second = self.resolve([subject, lte, ceil])
        return first & second

    def operate(self, a, operator, b):
        if operator.match(t.Token.Keyword, 'OR'):
            return a | b
        if operator.match(t.Token.Keyword, 'AND'):
            return a & b

    def compare(self, subject, operator, predicate):
        key = subject.value
        key, cond = self.make_key(operator, key)
        kwargs = {}
        
        if predicate.ttype is t.Token.Literal.Number.Integer:
            kwargs[key] = int(predicate.value)
        elif isinstance(predicate, sql.Identifier):
            kwargs[key] = predicate.get_name()
        elif predicate.ttype is t.Token.Literal.String.Single:
            v = predicate.value
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
