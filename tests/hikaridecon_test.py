#! /usr/bin/python
# -*- coding:utf-8 -*-
import unittest
import sys
import os
sys.path.append(os.pardir)
import omero_import

class TestHikariDecon(unittest.TestCase) :

    def setUp(self):
        self.path = '/data2/suguru/test/sample_R3D.dv'
        self.proc = omero_import.hikaridecon.run(self.path)

    def test_run(self):
        self.assertIsNotNone(self.proc)

    def test_product_path(self):
        self.assertIsNotNone(self.proc)
        self.assertEqual(self.proc.product_path, self.path+'_decon')

    def test_wait(self):
        self.assertIsNotNone(self.proc)
        self.proc.wait()
        self.assertEqual(self.proc.returncode, 0)

if __name__ == '__main__':
    unittest.main()
