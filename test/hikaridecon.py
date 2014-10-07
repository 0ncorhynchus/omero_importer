#! /usr/bin/python
# -*- coding:utf-8 -*-
import unittest
from omero_import import hikaridecon

class TestHikariDeconFunctions(unittest.TestCase):
    def setUp(self):
        self.path = '/data5/suguru/test/sample_R3D.dv'

    def test_check_size(self):
        self.assertTrue(hikaridecon.check_size(self.path,
            500 * 1024 * 1024)[1])
        self.assertFalse(hikaridecon.check_size(self.path,
            400 * 1024 * 1024)[1])

class TestHikariDecon(unittest.TestCase):

    def setUp(self):
        self.path = '/data5/suguru/test/sample_R3D.dv'
        self.proc = hikaridecon.run(self.path)

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
