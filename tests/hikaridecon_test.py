#! /usr/bin/python
# -*- coding:utf-8 -*-
import unittest
import sys
import os
sys.path.append(os.pardir)
import hikaridecon

class TestHikariDecon(unittest.TestCase) :

    def setUp(self):
        self.path = '/data2/suguru/test/sample_R3D.dv'

    def test_run(self):
        proc = hikaridecon.run(self.path)
        self.assertIsNotNone(proc)

    def test_product_path(self):
        proc = hikaridecon.run(self.path)
        self.assertEqual(proc.product_path, self.path+'_decon')

    def test_wait(self):
        proc = hikaridecon.run(self.path)
        self.assertIsNotNone(proc)
        proc.wait()
        self.assertEqual(proc.returncode, 0)

if __name__ == '__main__':
    unittest.main()
