# -*- coding: utf-8 -*-

import unittest
import sys
import os
sys.path.append(os.path.join(os.pardir,'omero_import'))
from functions import *

class TestFunctions(unittest.TestCase):

    def test_always(self):
        self.assertEqual(always(42)(), 42)
        self.assertTrue(always(True)())
        self.assertFalse(always(False)())

    def test_concat(self):
        list0 = ['a', 'b', 'c']
        list1 = [1, 2, 3, 4, 5]
        list2 = ['spam', 'ham']
        self.assertEqual(concat(list0, list1),
                ['a', 'b', 'c', 1, 2, 3, 4, 5])
        self.assertEqual(concat(list0, list1, list2),
                ['a', 'b', 'c', 1, 2, 3, 4, 5, 'spam', 'ham'])

    def test_construct(self):
        list0 = ['a', 'b', 'c']
        tail = 'd'
        self.assertEqual(construct(list0, tail),
                ['a', 'b', 'c', 'd'])

    def test_partial(self):
        true = partial(always, True)()
        self.assertTrue(true())
        add = lambda x, y: x + y
        add10 = partial(add, 10)
        self.assertEqual(add10(50), 60)
        def spam(key, **kwargs):
            default = {key: 'default'}
            default.update(kwargs)
            return default[key]
        ham = partial(spam, 'ham')
        self.assertEqual(ham(ham='hoge'), 'hoge')
        self.assertNotEqual(ham(hoge='hoge'), 'hoge')

    def test_isNone(self):
        self.assertTrue(isNone(None))
        self.assertFalse(isNone({}))
        self.assertFalse(isNone([]))
        self.assertFalse(isNone(0))

    def test_isNotNone(self):
        self.assertFalse(isNotNone(None))
        self.assertTrue(isNotNone({}))
        self.assertTrue(isNotNone([]))
        self.assertTrue(isNotNone(0))

    def test_fail(self):
        with self.assertRaises(IOError) as cm:
            fail(IOError, 36, "exception message")
        the_exception = cm.exception
        self.assertEqual(the_exception.errno, 36)

if __name__ == '__main__':
    unittest.main()
