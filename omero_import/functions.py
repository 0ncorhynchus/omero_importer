# -*- coding: utf-8 -*-
from __future__ import print_function
from functools import reduce
from sys import stderr

always = lambda val: lambda: val
concat = lambda *arrays: reduce(lambda array, n: array + n, arrays)
construct = lambda array, tail: concat(array, [tail])
partial = lambda fun, *args: lambda *rest, **kwargs: fun(*concat(args, rest), **kwargs)
isNone = lambda obj: obj is None
isNotNone = lambda obj: not isNone(obj)
log = lambda *args: print(*concat(['[LOG]\t'], list(args)), file=stderr)

def fail(error, *args):
    raise error(*args)

