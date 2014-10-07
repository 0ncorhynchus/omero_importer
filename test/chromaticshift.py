# -*- coding: utf-8 -*-
import unittest
import os
from omero_import import ChromaticShift, ChromaticShiftError

class TestChromaticShift(unittest.TestCase):

    def setUp(self):
        self.invalid_filename = 'sample_R3D.dv_decon'
        self.filename = '/data5/suguru/test/sample_R3D.dv_decon'
        self.shift = ChromaticShift(self.filename)

    def test_constructor(self):
        with self.assertRaises(ChromaticShiftError):
            error_shift = ChromaticShift(self.invalid_filename)

    def test_is_already_done(self):
        self.assertFalse(self.shift.is_already_done('/data5/suguru/sample_R3D.dv_decon.zs'))
        self.assertTrue(self.shift.is_already_done('/data5/suguru/test/sample_R3D.dv_decon.zs'))

    def test_path(self):
        self.assertNotEqual(self.shift.path, '')

    def test_filename(self):
        self.assertNotEqual(self.shift.filename, '')

    def test_do(self):
        try:
            self.shift.do()
        except ChromaticShiftError, err:
            print >> sys.stderr, err
        self.assertTrue(os.path.exists(self.shift.path))
        os.remove(self.shift.path)

if __name__ == '__main__':
    unittest.main()
