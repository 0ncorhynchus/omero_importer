# -*- coding: utf-8 -*-

partial = lambda fun, head: lambda *args: fun(head, args)
isNone = lambda obj: obj is None
isNotNone = lambda obj: not isNone(obj)

def fail(error, *args):
    raise error(*args)
