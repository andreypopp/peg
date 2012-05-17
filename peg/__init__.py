"""

    peg -- parsing expression grammar
    =================================

"""

__all__ = ("seq", "item", "rep", "ref", "opt", "bracketed", "binop")

class ParseError(Exception):

    def __init__(self, p, string):
        super(ParseError, self).__init__(p, string)
        self.p = p
        self.string = string

class Parser(object):

    action = None

    def __call__(self, string):
        raise NotImplementedError()

    def __gt__(self, action):
        return self.set_action(action)

    def set_action(self, action):
        if self.action is not None:
            oldaction = self.action
            self.action = lambda *a, **kw: action(oldaction(*a, **kw))
        else:
            self.action = action
        return self

    def __or__(self, p):
        return Choice(self, p)

    def parse(self, string):
        result, string = self(string)
        if string:
            raise ParseError(self, string)
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
        raise ParseError(self, string)

class NotPredicate(Parser):

    def __init__(self, p):
        self.p = p

    def __call__(self, string):
        try:
            self.p(string)
        except ParseError:
            return None, string
        else:
            raise ParseError(self, string)

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
            raise ParseError(self, string)
        r = self.item if self.action is None else self.action(self.item)
        return r, string[1:]

class Ref(Parser):

    def define(self, p):
        self.p = p

    def __call__(self, string):
        return self.p(string)

seq = Sequence
rep = Repetition
item = Item
ref = Ref
opt = Optional

def bracketed(l, r):
    """ Parser for bracketed expressions"""
    return lambda p: seq(l, p, r) > (lambda (_l, p, _r): p)

def binop(arg, op):
    """ Parser for binary operations"""
    makebin = lambda (arg, ops): (
        arg if not ops
        else reduce(lambda a, (op, b): (a, op, b), ops, arg))
    return seq(arg, rep(seq(op, arg))) > makebin
