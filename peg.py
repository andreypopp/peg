"""

    peg -- parsing expression grammar
    =================================

"""

__all__ = ()

class ParseError(Exception):
    pass

class ref(object):

    def define(self, p):
        self.p = p

    def __call__(self, text):
        return self.p(text)

def char(s):
    def parser(text):
        if text[:len(s)] != s:
            raise ParseError()
        return s, text[len(s):]
    return parser

def zero_or_more(p):
    def parser(text):
        result = []
        while True:
            try:
                r, text = p(text)
                result.append(r)
            except ParseError:
                return result, text
    return parser

def sequence(*ps):
    def parser(text):
        result = []
        for p in ps:
            r, text = p(text)
            result.append(r)
        return result, text
    return parser

def one_or_more(p):
    return sequence(p, zero_or_more(p))

def optional(p):
    def parser(text):
        try:
            result, text = p(text)
        except ParseError:
            return None, text
        else:
            return result, text
    return parser

def choice(*ps):
    def parser(text):
        for p in ps:
            try:
                return p(text)
            except ParseError:
                continue
        raise ParseError()
    return parser

def not_predicate(p):
    def parser(text):
        try:
            p(text)
        except ParseError:
            return None, text
        else:
            raise ParseError()
    return parser

def and_predicate(p):
    def parser(text):
        p(text)
        return None, text
    return parser

def parse(p, text, suppress_error=False):
    try:
        result, text = p(text)
        if text:
            raise ParseError()
    except ParseError:
        if suppress_error:
            return None
        raise
    return result

if __name__ == "__main__":
    id = choice(char('a'), char('b'))
    op = choice(char('+'), char('-'))
    expr = ref()
    val = choice(id, sequence(char('('), expr, char(')')))
    bin = sequence(val, zero_or_more(sequence(op, val)))
    expr.define(bin)
    start = expr

    print parse(start, 'a', suppress_error=True)
    print parse(start, 'a+b', suppress_error=True)
    print parse(start, '(a+b)', suppress_error=True)
    print parse(start, 'a+(a+b)', suppress_error=True)
    print parse(start, 'a+(a+(a+b))', suppress_error=True)
    print parse(start, 'a+(a+(a+b))+a', suppress_error=True)
