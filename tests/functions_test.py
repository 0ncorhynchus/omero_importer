# -*- coding: utf-8 -*-

import unittest
import sys
import os
sys.path.append(os.path.join(os.pardir,'omero_import'))
from functions import *

class TestFunctions(unittest.TestCase):

    def test_fail(self):
        with self.assertRaises(IOError) as cm:
            fail(IOError, 36, "exception message")

        the_exception = cm.exception
        self.assertEqual(the_exception.errno, 36)

if __name__ == '__main__':
    unittest.main()
