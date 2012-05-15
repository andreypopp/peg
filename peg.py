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

    def parse(self, string):
        result, string = self(string)
        if string:
            raise ParseError()
        return result

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

class Ref(Parser):

    def define(self, p):
        self.p = p

    def __call__(self, string):
        return self.p(string)

seq = Sequence
rep = Repetition
pat = Pattern
item = Item
ref = Ref

if __name__ == "__main__":

    makebin_    = lambda l, ls: reduce(lambda a, (op, b): (a, op, b), ls, l)
    makebin     = lambda (l, ls): l if not ls else makebin_(l, ls)

    expr    = ref()
    num     = pat("[0-9]+")                         > int
    bexpr   = seq(item("("), expr, item(")"))       > (lambda (_a, e, _b): e)
    val     = num | bexpr
    mulop   = pat("\*|/")
    addop   = pat("\-|\+")
    prod    = seq(val, rep(seq(mulop, val)))        > makebin
    sum     = seq(prod, rep(seq(addop, prod)))      > makebin
    expr.define(sum)

    print expr.parse('1')
    print expr.parse('1+2')
    print expr.parse('1+2+3')
    print expr.parse('1*2')
    print expr.parse('1*2+3')
    print expr.parse('(1*2)+3')
    print expr.parse('1*(2+3)')
    print expr.parse('1*(2+3)-3')
