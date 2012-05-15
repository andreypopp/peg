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
                result.append(r if self.action is None else self.action(r))
            except ParseError:
                return result, string

class Sequence(Parser):

    def __init__(self, *ps):
        self.ps = ps

    def __call__(self, string):
        result = []
        for p in self.ps:
            r, string = p(string)
            result.append(r if self.action is None else self.action(r))
        return result, string

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

def parse(p, string, suppress_error=False):
    try:
        result, string = p(string)
        if string:
            raise ParseError()
    except ParseError:
        if suppress_error:
            return None
        raise
    return result

if __name__ == "__main__":

    class Id(object):
        def __init__(self, name):
            self.name = name
        def __repr__(self):
            return "Id(%s)" % self.name

    id = Pattern("[a-zA-Z_][a-zA-Z_0-9]*") > Id
    op = Item('+') | Item('-')
    expr = Ref()
    val = id | Sequence(Item('('), expr, Item(')'))
    bin = Sequence(val, Repetition(Sequence(op, val)))
    expr.define(bin)
    start = expr

    print parse(start, 'a', suppress_error=True)
    print parse(start, 'a+b', suppress_error=True)
    print parse(start, '(a+b)', suppress_error=True)
    print parse(start, 'a+(a+b)', suppress_error=True)
    print parse(start, 'a+(a+(a+c))', suppress_error=True)
    print parse(start, 'a+(a+(a+b))+a', suppress_error=True)
    print parse(start, 'a+(a+(a+d))+a', suppress_error=True)
