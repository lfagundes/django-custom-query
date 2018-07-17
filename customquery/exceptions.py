class FieldDoesNotExist(Exception):
    def __init__(self, field):
        self.field = field
        super().__init__("Field '%s' does not exist" % field)

class ParenthesisDontMatch(Exception):
    def __init__(self):
        super().__init__("Parenthesis do not match")

class UnknownOperator(Exception):
    def __init__(self, operator):
        self.operator = operator
        super().__init__("Operator '%s' is invalid" % operator)
