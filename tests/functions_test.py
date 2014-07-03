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

    def test_update(self):
        self.assertEqual(update({},{}),{})
        self.assertEqual(update({}),{})
        self.assertEqual(update({}, {'test': 'sample'}), {'test': 'sample'})
        self.assertEqual(update({}, {'test': 'sample'}), {'test': 'sample'}, {})
        self.assertEqual(update({'test': 'sample'}, {'tmp': 'tmp'}),
                {'test': 'sample', 'tmp': 'tmp'})

    def test_fail(self):
        with self.assertRaises(IOError) as cm:
            fail(IOError, 36, "exception message")

        the_exception = cm.exception
        self.assertEqual(the_exception.errno, 36)

if __name__ == '__main__':
    unittest.main()
