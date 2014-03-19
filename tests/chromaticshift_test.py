# -*- coding: utf-8 -*-
import unittest
import sys
import os
sys.path.append(os.pardir)
from chromaticshift import ChromaticShift, ChromaticShiftError

class TestChromaticShift(unittest.TestCase):

    def setUp(self):
        self.invalid_filename = '2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv_decon'
        self.filename = '/data2/gkafer/Exp49/2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv_decon'
        self.shift = ChromaticShift(self.filename)

    def test_constructor(self):
        with self.assertRaises(ChromaticShiftError):
            error_shift = ChromaticShift(self.invalid_filename)

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
