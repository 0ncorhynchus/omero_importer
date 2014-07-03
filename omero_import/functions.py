# -*- coding: utf-8 -*-
from functools import reduce

always = lambda val: lambda: val
partial = lambda fun, head: lambda *args: fun(head, args)
isNone = lambda obj: obj is None
isNotNone = lambda obj: not isNone(obj)

def update(*objs):
    retval = {}
    for obj in objs:
        retval.update(obj)
    return retval

def fail(error, *args):
    raise error(*args)

