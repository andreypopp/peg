from peg import *
from collections import namedtuple

Select          = namedtuple("Select", ["select_list", "from_clause"])
From            = namedtuple("From", ["table", "joins"])
_Ref            = namedtuple("Ref", ["parts"])
Join            = namedtuple("Join", ["table"])
AllColumns      = namedtuple("AllColumns", [])

class Ref(_Ref):
    def __str__(self):
        return "Ref(%s)" % ".".join(self.parts)

    __repr__ = __str__

o               = lambda p: opt(seq(ws, p))     > (lambda (_ws, p): p)
sep             = lambda p, s: seq(
    p,
    rep(seq(s, p))                              > (lambda ls: [y for x, y in ls])
    )                                           > (lambda (l, ls): [l] + ls)
wsep            = lambda p, s: seq(
    p,
    rep(seq(ows, s, ows, p))                    > (lambda ls: [y for _, x, _, y in ls])
    )                                           > (lambda (l, ls): [l] + ls)
ws              = pat("\s+")
ows             = pat("\s*")
comma           = item(',')
dot             = item('.')
star            = item('*')                     > (lambda x: AllColumns())
id              = pat("[a-zA-Z_]+")

ref             = sep(id, dot)                  > Ref
select_elem     = star | ref
select_list     = wsep(select_elem, comma)
join_clause     = seq(pat("join"), ws, ref)     > (lambda (_kw, _ws, t): Join(t))
join_list       = sep(join_clause, ws)
from_list       = sep(ref, comma)
from_clause     = seq(pat("from"), ws, from_list, o(join_list)) > (lambda (_kw, _ws, t, j): From(t, j))
select_stmt     = seq(
    pat("select"), ws,
    select_list,
    o(from_clause))                             > (lambda (_kw, _ws, sl, f): Select(sl, f))
stmt            = select_stmt

tests = [
    'select a',
    'select  a',
    'select a,v',
    'select *',
    'select *,a.b.c',
    'select a from a',
    'select a from a join b join b',
    ]

for test in tests:
    print test
    print stmt.parse(test)
