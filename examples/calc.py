from peg import ref, pat, oneof, seq, rep, item

makebin_    = lambda l, ls: reduce(lambda a, (op, b): (a, op, b), ls, l)
makebin     = lambda (l, ls): l if not ls else makebin_(l, ls)

expr    = ref()
num     = pat("[0-9]+")                         > int
bexpr   = seq(item("("), expr, item(")"))       > (lambda (_a, e, _b): e)
val     = num | bexpr
mulop   = oneof("*/")
addop   = oneof("+-")
prod    = seq(val, rep(seq(mulop, val)))        > makebin
sum     = seq(prod, rep(seq(addop, prod)))      > makebin
expr.define(sum)

def e(x):
    ops = {
        "+": int.__add__,
        "-": int.__sub__,
        "*": int.__mul__,
        "/": int.__truediv__,
        }
    if isinstance(x, tuple):
        l, op, r = x
        return ops[op](e(l), e(r))
    else:
        return x

tests = [
    '1',
    '1+2',
    '1+2+3',
    '1*2',
    '1*2+3',
    '(1*2)+3',
    '1*(2+3)',
    '1*(2+3)-3',
    ]
for test in tests:
    print test, "=", e(expr.parse(test))
