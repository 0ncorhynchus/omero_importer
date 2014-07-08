# -*- coding: utf-8 -*-
from functools import reduce

always = lambda val: lambda: val
concat = lambda *arrays: reduce(lambda array, n: array + n, arrays)
construct = lambda array, tail: concat(array, [tail])
partial = lambda fun, *args: lambda *rest, **kwargs: fun(*concat(args, rest), **kwargs)
isNone = lambda obj: obj is None
isNotNone = lambda obj: not isNone(obj)

def fail(error, *args):
    raise error(*args)

