from sqlparse import parse, tokens as t, sql
from datetime import datetime, date
from django.core import exceptions as django_exceptions
from . import exceptions
from django.db.models import fields, Q, F, QuerySet

class Parser:

    def __init__(self, model, date_format='%Y-%m-%d'):
        self.model = model
        self.date_format = date_format
        self.extra_params = dict(cones=[])

    def parse(self, query):
        """Parse SQL-like condition statements and return Django Q objects"""

        parsed = parse(query)[0]
        return self._resolve(parsed.tokens)

    def _resolve(self, tokens):
        tokens = self._strip_whitespaces(tokens)

        # Simple case of one token.
        if len(tokens) == 1:
            if isinstance(tokens[0], sql.Function):
                # Cone-search function
                return self._cone(tokens[0])
            else:
                return self._resolve(tokens[0])

        # Parsing internals of parenthesis totken.
        if tokens[0].match(t.Token.Punctuation, '('):
            tokens = self._get_group(tokens)

        # Catch cases of numerous AND OR statements.

        # AND has higher rang than OR, so AND should be resolved last
        for i in reversed(range(len(tokens))):
            
            if tokens[i].match(t.Keyword, 'OR'):
                return self._resolve(tokens[:i]) | self._resolve(tokens[i+1:])

        for i in reversed(range(len(tokens))):
            if tokens[i].match(t.Keyword, 'AND'):
                # avoid AND in BETWEEN clause
                betweenIsThere = True in [tok.match(t.Keyword, 'BETWEEN') for tok in tokens]
                if not betweenIsThere or i<=2:
                    return self._resolve(tokens[:i]) & self._resolve(tokens[i+1:])
                if i>2:
                    if not tokens[i-2].match(t.Keyword, 'BETWEEN'):
                        return self._resolve(tokens[:i]) & self._resolve(tokens[i+1:])

        # Treat between clause
        for i, tok in enumerate(tokens):
            if tok.match(t.Keyword, 'BETWEEN'):
                if len(tokens) == 5:
                    # only BETWEEN clause (param BETWEEN a AND b)
                    return self._between(tokens[i-1], tokens[i+1], tokens[i+3])
                else:
                    raise exceptions.InvalidQuery()

        operator = tokens[1]
        
        if operator.match(t.Comparison, ['IN', 'in', 'In', 'iN']):
            return self._in(tokens[0], tokens[2])

        # this strange regex covers plenty of vairants 'NOT IN', 'Not    In', etc
        if operator.match(t.Comparison, r'(?i)\bNOT +IN\b', regex=True):
            return ~self._in(tokens[0], tokens[2])

        if operator.ttype is t.Token.Keyword:
            # if operator.match(t.Token.Keyword, 'BETWEEN'):
            #     assert(len(tokens) == 5)
            #     return self._between(tokens[0], tokens[2], tokens[4])
            if operator.match(t.Token.Keyword, 'NOT'):
                if len(tokens) == 3:
                    return self._compare(*tokens)
                if len(tokens) == 4 and tokens[2].match(t.Token.Keyword, 'IN'):
                    return ~self._in(tokens[0], tokens[3])
                raise exceptions.InvalidQuery()

            if operator.match(t.Token.Keyword, 'IS'):
                return self._is(tokens[0], tokens[2])
            else:
                a = self._resolve(tokens[0])
                b = self._resolve(tokens[2])
                return self._operate(a, tokens[1], b)
        else:
            if len(tokens) > 3:
                raise exceptions.InvalidQuery()
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

    def _is(self, subject, values):
        if values.match(t.Token.Keyword, 'NULL'):
            kwargs = {
                '%s__isnull' % subject.value: True,
            }
        elif values.match(t.Token.Keyword, 'NOT NULL'):
            kwargs = {
                '%s__isnull' % subject.value: False,
            }
        else:
            raise exceptions.InvalidIsParameter(values.value)
        return Q(**kwargs)

    def _operate(self, a, operator, b):
        if operator.match(t.Token.Keyword, 'OR'):
            return a | b
        if operator.match(t.Token.Keyword, 'AND'):
            return a & b

    def _compare(self, subject, operator, predicate):
        # Raise exception if field does not exist
        if type(subject) is sql.Operation:
            "This is the case of math expression as a subject."
            subject_tokens = self._strip_whitespaces(subject.tokens)
            subject_operator = subject_tokens[1]
            subject_subject = subject_tokens[0]
            subject_predicate = subject_tokens[2]
            key, cond = self._make_key(operator, subject_subject.value)

            # this is a bit off the logic line, but it works than second
            # term in expression field name or related field
            value_subject_predicate = subject_predicate.value.replace(".", "__")
            value_predicate = self._get_value(subject_subject.value, predicate)

            kwargs = {}
            if subject_operator.value == '+':
                kwargs[key] = value_predicate - F(value_subject_predicate)
            elif subject_operator.value == '-':
                kwargs[key] = value_predicate + F(value_subject_predicate)
            elif subject_operator.value == '*':
                kwargs[key] = value_predicate / F(value_subject_predicate)
            elif subject_operator.value == '/':
                kwargs[key] = value_predicate * F(value_subject_predicate)
        else:
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
        if predicate.ttype is t.Token.Literal.Number.Float:
            return float(v)
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
        if op.match(comp, '~'):
            return [key + '__icontains', True]
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

    def _cone(self, tokens):
        if isinstance(tokens[0], sql.Identifier):
            tname = tokens[0].get_name().lower()
            if tname == 'cone':
                # remove parentheses
                tokens_nopars = self._get_group(tokens[1])[0]
                # remove whitespaces and punctuation
                cone_values = [ tok for tok in tokens_nopars if (not tok.ttype is t.Token.Text.Whitespace) and (not tok.ttype is t.Token.Punctuation)]
        
                if len(cone_values) != 3:
                    raise exceptions.InvalidConeArguments
                else:
                    # This is a weird way returning Cone query parameters that will be 
                    # used to annotate the corresponding Django model

                    cone_params = dict(
                        cone_ra = float(cone_values[0].value),
                        cone_dec = float(cone_values[1].value),
                        cone_radius = float(cone_values[2].value),
                        )

                    # Check whether this is the first Cone statement or 
                    # there are already several in the query.
                    cone_index = len(self.extra_params['cones'])
                    cone_index_str = "" if cone_index == 0 else str(cone_index)

                    # Extend dictionary with Cone parameters
                    self.extra_params['cones'].append(cone_params)

                    # Build and return corresponding Django Q object with boolean
                    # statement cone_query=1 or cone_query1=1 etc
                    kwargs = dict()
                    kwargs[f"cone_query{cone_index_str}"] = True

                    return Q(**kwargs)
            else:
                raise exceptions.InvalidFunction(tname)
        else:
            raise exceptions.InvalidQuery()
