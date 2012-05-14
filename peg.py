"""

    peg -- parsing expression grammar
    =================================

"""

__all__ = ()

class ParseError(Exception):
    pass

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
    op = choice(char('+'), char('-'))
    id = choice(char('a'), char('b'))
    expr = choice(sequence(id, op, id), id)
    start = expr

    print parse(start, 'a+b', suppress_error=True)
    print parse(start, 'a+', suppress_error=True)
    print parse(start, 'a', suppress_error=True)
    print parse(start, '', suppress_error=True)
