# -*- coding: utf-8 -*-
import unittest
import sys
import os
import re
sys.path.append(os.pardir)
from omero_importer import *

class TestOmeroImporter(unittest.TestCase):

    def setUp(self):
        self.dirpath = '/data5/suguru/test'
        self.filepath = '/data5/suguru/test/sample_R3D.dv_decon'
        self.pattern = re.compile('(.*)_decon')

    def test_search_files(self):
        files = search_files(self.dirpath, self.pattern)
        self.assertNotEqual(len(files), 0)
        for f in files:
            self.assertTrue(os.path.exists(f))
            self.assertTrue(f[-6:], '_decon')

    def test_get_owner(self):
        owner = get_owner(self.dirpath)
        self.assertEqual(owner, 'suguru')
        owner = get_owner(self.filepath)
        self.assertEqual(owner, 'suguru')

    def test_close_session(self):
        kwargs = {}
        kwargs['conn'] = tools.connect_to_omero('suguru', 'omx')
        self.assertTrue(kwargs['conn'].connect())
        kwargs['conn']._closeSession()

    def test_connect(self):
        kwargs = {
                'uname': 'suguru',
                'passwd': 'omx',
                'dirname': self.dirpath
                }
        connected = connect(**kwargs)
        self.assertTrue('conn' in connected)
        close_session(**connected)

    def test_init_chromatic_shift(self):
        kwargs = init_chromatic_shift(path=self.filepath)
        self.assertTrue('zs' in kwargs)

    def test_check_not_imported_yet(self):
        kwargs = {
                'uname': 'suguru',
                'passwd': 'omx',
                'path': self.filepath,
                'dirname': self.dirpath
                }
        connected = init_chromatic_shift(**connect(**kwargs))
        with self.assertRaises(EnvironmentError) as cm:
            check_not_imported_yet(**connected)

    def test_get_log(self):
        kwargs = {
                'path' : self.filepath,
                'dirname' : self.dirpath,
                'zs': ChromaticShift(self.filepath)
                }
        with self.assertRaises(ValueError):
            get_log(path=self.dirpath)
        try:
            logpath = get_log(**kwargs)['logfile']
        except IOError, err:
            self.fail(err)
        self.assertTrue(os.path.exists(logpath))

    def test_succeed(self):
        succeeded = succeed(path=self.filepath)
        self.assertTrue('retval' in succeeded)
        self.assertTrue('SUCCESS' in succeeded['retval'])
        self.assertTrue(succeeded['retval']['SUCCESS'])
        self.assertTrue('path' in succeeded)
        self.assertEqual(succeeded['path'], self.filepath)

    def test_unit_process(self):
        kwargs = {'retval': {'PROCESSES': []}}
        prcname = 'UNIT TEST'
        processed = unit_process(prcname, lambda **kwargs: kwargs, **kwargs)
        self.assertEqual(processed['retval']['PROCESSES'], [prcname])
        with self.assertRaises(EnvironmentError) as cm:
            unit_process(prcname,
                    lambda **kwargs: fail(EnvironmentError, 'the EnvironmentError in the process %s' % prcname),
                    **kwargs)

    def test_import_file(self):
        result = import_file(self.dirpath) # this is not a file but a directory
        self.assertFalse(result[1])
        result = import_file(self.filepath) # this file has already been imported
        self.assertTrue(result[1])

if __name__ == '__main__':
    unittest.main()
