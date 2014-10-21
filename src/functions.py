# -*- coding: utf-8 -*-
from functools import reduce
import sys

always = lambda val: lambda: val
concat = lambda *arrays: reduce(lambda array, n: array + n, arrays)
construct = lambda array, tail: concat(array, [tail])
partial = lambda fun, *args: lambda *rest, **kwargs: fun(*concat(args, rest), **kwargs)
isNone = lambda obj: obj is None
isNotNone = lambda obj: not isNone(obj)

def fail(error, *args):
    raise error(*args)

def log(tag, out, obj):
    string = "%-10s %s" % ('[' + tag + ']', str(obj))
    print >> out, string
    out.flush()
    return string

info = partial(log, 'INFO', sys.stderr)
error = partial(log, 'ERROR', sys.stderr)
