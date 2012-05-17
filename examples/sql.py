from peg import *
from peg.text import *
from collections import namedtuple

Select          = namedtuple("Select",
    ["select_list", "from_clause", "where_clause", "offset_clause", "limit_clause"])
From            = namedtuple("From", ["table", "joins"])
_Ref            = namedtuple("Ref", ["parts"])
Join            = namedtuple("Join", ["table", "condition"])
AllColumns      = namedtuple("AllColumns", [])
UsingJoinCond   = namedtuple("UsingJoinCond", ["columns"])
OnJoinCond      = namedtuple("OnJoinCond", ["condition"])
Where           = namedtuple("Where", ["condition"])
Offset          = namedtuple("Offset", ["n"])
Limit           = namedtuple("Limit", ["n"])
BinOp           = namedtuple("BinOp", ["left", "op", "right"])
Null            = namedtuple("Null", [])

class Ref(_Ref):
    def __str__(self):
        return "Ref(%s)" % ".".join(self.parts)

    __repr__ = __str__

cbracketed      = bracketed(item('('), item(')'))
wspaced         = bracketed(ws, ws)
o               = lambda p: opt(seq(ws, p))     > (lambda (_ws, p): p)
sep             = lambda p, s: seq(
    p,
    rep(seq(s, p))                              > (lambda ls: [y for x, y in ls])
    )                                           > (lambda (l, ls): [l] + ls)
wsep            = lambda p, s: seq(
    p,
    rep(seq(ows, s, ows, p))                    > (lambda ls: [y for _, x, _, y in ls])
    )                                           > (lambda (l, ls): [l] + ls)
comma           = item(',')
dot             = item('.')
star            = item('*')                     > (lambda x: AllColumns())
id              = pat("[a-zA-Z_]+")
num             = pat("[0-9]+")                 > int
null            = pat("null")                   > (lambda x: Null())
literal         = num | null

idref           = sep(id, dot)                   > Ref
id_list         = wsep(id, comma)                > (lambda ids: map(Ref, ids))

expr            = ref()
expr0           = idref | literal | cbracketed(expr)
expr1           = binop(expr0, wspaced(oneof("*/%")))
expr2           = binop(expr1, wspaced(oneof("+-")))
expr3           = binop(expr2, wspaced(pat("is")))
expr4           = binop(expr3, wspaced(pat("like") | pat("ilike")))
expr5           = binop(expr4, wspaced(oneof("<>")))
expr6           = binop(expr5, wspaced(item("=")))
expr7           = binop(expr6, wspaced(pat("and")))
expr8           = binop(expr7, wspaced(pat("or")))
expr.define(expr8)

where_clause    = seq(pat("where"), ws, expr)                   > (lambda (_kw, _ws, c): Where(c))
offset_clause   = seq(pat("offset"), ws, num)                   > (lambda (_kw, _ws, n): Offset(n))
limit_clause   = seq(pat("limit"), ws, num)                     > (lambda (_kw, _ws, n): Limit(n))

select_elem     = star | idref
select_list     = wsep(select_elem, comma)

join_cond_using = seq(pat("using"), ows, cbracketed(id_list))    > (lambda (_kw, _ws, r): UsingJoinCond(r))
join_cond_on    = seq(pat("on"), ws, expr)                      > (lambda (_kw, _ws, c): OnJoinCond(c))
join_cond       = join_cond_using | join_cond_on
join_clause     = seq(pat("join"), ws, idref, ws, join_cond)    > (lambda (_kw, _ws, t, _ws2, cond):Join(t, cond))
join_list       = sep(join_clause, ws)

from_list       = sep(idref, comma)
from_clause     = seq(pat("from"), ws, from_list, o(join_list)) > (lambda (_kw, _ws, t, j): From(t, j))

select_stmt     = seq(
    pat("select"), ws,
    select_list,
    o(
        seq(from_clause,
            o(where_clause),
            o(offset_clause),
            o(limit_clause))
        )) > (lambda (_kw, _ws, sl, fw): (
            Select(sl, None, None, None, None) if not fw
            else Select(sl, fw[0], fw[1], fw[2], fw[3])))

stmt            = select_stmt

tests = [
    'select a',
    'select  a',
    'select a,v',
    'select *',
    'select *,a.b.c',
    'select a from a',
    'select a from a join b using(a, b) join c on d and c and (f or e)',
    'select a from a join b on 1 > a and 2 = c',
    'select a from a where a.c = 2',
    'select a from a join b on a.c = b.d where a.c = 2',
    'select a from a limit 10',
    'select a from a offset 10',
    'select a from a offset 10 limit 20',
    ]

for test in tests:
    print test
    print stmt.parse(test)
