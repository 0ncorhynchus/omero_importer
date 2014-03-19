# -*- coding: utf-8 -*-
import unittest
import sys
import os
import re
sys.path.append(os.pardir)
from omero_importer import *

class TestOmeroImporter(unittest.TestCase):

    def setUp(self):
        self.dirpath = '/data2/gkafer/Exp49/'
        self.filepath = '/data2/gkafer/Exp49/2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv_decon'
        self.pattern = re.compile('(.*)_decon')

    def test_search_files(self):
        files = search_files(self.dirpath, self.pattern)
        self.assertNotEqual(len(files), 0)
        for f in files:
            self.assertTrue(os.path.exists(f))
            self.assertTrue(f[-6:], '_decon')

    def test_get_log(self):
        with self.assertRaises(ValueError):
            get_log(self.dirpath)
        try:
            logpath = get_log(self.filepath)
        except IOError, err:
            self.fail(err)
        self.assertTrue(os.path.exists(logpath))

    def test_get_owner(self):
        owner = get_owner(self.dirpath)
        self.assertEqual(owner, 'gkafer')
        owner = get_owner(self.filepath)
        self.assertEqual(owner, 'gkafer')

    def test_import_file(self):
        self.assertFalse(import_file(self.dirpath)) # this is not a file but a directory
        self.assertFalse(import_file(self.filepath)) # this file has already been imported

if __name__ == '__main__':
    unittest.main()
