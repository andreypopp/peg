"""

    peg -- parsing expression grammar
    =================================

"""

import re

__all__ = ()

class ParseError(Exception):
    pass

class Parser(object):

    action = None

    def __call__(self, string):
        raise NotImplementedError()

    def __gt__(self, action):
        self.action = action
        return self

    def __or__(self, p):
        return Choice(self, p)

class Repetition(Parser):

    def __init__(self, p):
        self.p = p

    def __call__(self, string):
        result = []
        while True:
            try:
                r, string = self.p(string)
                result.append(r)
            except ParseError:
                return (result if self.action is None else self.action(result),
                        string)

class Sequence(Parser):

    def __init__(self, *ps):
        self.ps = ps

    def __call__(self, string):
        result = []
        for p in self.ps:
            r, string = p(string)
            result.append(r)
        return (tuple(result) if self.action is None else self.action(result),
                string)

class Optional(Parser):

    def __init__(self, p):
        self.p = p

    def __call__(self, string):
        try:
            r, string = self.p(string)
            return r if self.action is None else self.action(r), string
        except ParseError:
            return None, string
        else:
            return result, string

class Choice(Parser):

    def __init__(self, *ps):
        self.ps = ps

    def __call__(self, string):
        for p in self.ps:
            try:
                r, string = p(string)
                return r if self.action is None else self.action(r), string
            except ParseError:
                continue
        raise ParseError()

class NotPredicate(Parser):

    def __init__(self, p):
        self.p = p

    def __call__(self, string):
        try:
            self.p(string)
        except ParseError:
            return None, string
        else:
            raise ParseError()

class AndPredicate(Parser):

    def __init__(self, p):
        self.p = p

    def __call__(self, string):
        self.p(string)
        return None, string

class Item(Parser):

    def __init__(self, item):
        self.item = item

    def __call__(self, string):
        if not string or string[0] != self.item:
            raise ParseError()
        r = self.item if self.action is None else self.action(self.item)
        return r, string[1:]

class Pattern(Parser):

    def __init__(self, pattern):
        pattern = "^(" + (pattern
            .replace("(", "\\(")
            .replace(")", "\\)")) + ")"
        self.pattern = re.compile(pattern)

    def __call__(self, string):
        m = self.pattern.match(string)
        if not m:
            raise ParseError()
        item = string[:m.end()]
        r = item if self.action is None else self.action(item)
        return r, string[m.end():]

class Ref(object):

    def define(self, p):
        self.p = p

    def __call__(self, string):
        return self.p(string)

def parse(p, string):
    result, string = p(string)
    if string:
        raise ParseError()
    return result

if __name__ == "__main__":

    class Op(object):
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return "Op(%s)" % self.name

    class Bin(object):
        def __init__(self, a, op, c):
            self.a, self.op, self.b = a, op, c
        def __repr__(self):
            return "Bin(%s, %s, %s)" % (self.a, self.op, self.b)

    expr = Ref()
    num = Pattern("[0-9]+") > int
    bexpr = Sequence(Item("("), expr, Item(")")) > (lambda (_a, e, _b): e)
    val = num | bexpr
    mulop = Pattern("\*|/")
    addop = Pattern("\-|\+")
    prod = Sequence(val, Repetition(Sequence(mulop, val))) > \
            (lambda (l, ls): l if not ls else reduce(
                lambda x, (op, y): Bin(x, op, y), ls, l))
    sum = Sequence(prod, Repetition(Sequence(addop, prod))) > \
            (lambda (l, ls): l if not ls else reduce(
                lambda x, (op, y): Bin(x, op, y), ls, l))
    expr.define(sum)
    start       = expr


    print parse(start, '1')
    print parse(start, '1+2')
    print parse(start, '1+2+3')
    print parse(start, '1*2')
    print parse(start, '1*2+3')
    print parse(start, '(1*2)+3')
    print parse(start, '1*(2+3)')
    print parse(start, '1*(2+3)-3')
