class FieldDoesNotExist(Exception):
    def __init__(self, field):
        self.field = field
        super().__init__("Field '%s' does not exist" % field)

class ParenthesisDontMatch(Exception):
    def __init__(self):
        super().__init__("Parenthesis do not match")

class ParenthesisExpected(Exception):
    def __init__(self, previous):
        super().__init__("Excepted opening parenthesis after %s" % previous)

class MalformedList(Exception):
    def __init__(self, previous):
        super().__init__("Values inside parenthesis are not a valid list")

class UnknownOperator(Exception):
    def __init__(self, operator):
        self.operator = operator
        super().__init__("Operator '%s' is invalid" % operator)

class InvalidQuery(Exception):
    def __init__(self):
        super().__init__("Invalid query")
