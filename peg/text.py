"""

    peg.text -- parsing text with peg
    =================================

"""

import re

from peg import Parser, ParseError

__all__ = (
    "pat", "oneof", "word", "ws", "ows", "id", "integer",
    "positive_integer", "negative_integer")

class Pattern(Parser):

    def __init__(self, pattern):
        pattern = "^(" + (pattern
            .replace("(", "\\(")
            .replace(")", "\\)")) + ")"
        self.pattern = re.compile(pattern)

    def __call__(self, string):
        m = self.pattern.match(string)
        if not m:
            raise ParseError(self, string)
        item = string[:m.end()]
        r = item if self.action is None else self.action(item)
        return r, string[m.end():]

    def __str__(self):
        return "<Pattern '%s'>" % self.pattern.pattern

    __repr__ = __str__

pat = Pattern

def oneof(chars):
    """ Shortcut for definining one of patterns"""
    return Pattern("[" + re.escape(chars) + "]")

def word(chars):
    return Pattern(re.escape(chars))

ws                  = pat("\s+")
ows                 = pat("\s*")
id                  = pat("[a-zA-Z_][a-zA-Z0-9_]*")
positive_integer    = pat("\+?[0-9]+")                  > int
negative_integer    = pat("\-[0-9]+")                   > int
integer             = pat("[\-\+]*[0-9]+")              > int
