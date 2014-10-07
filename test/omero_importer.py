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
        self.filepath = '/data5/suguru/test/sample_R3D.dv'
        self.deconpath = '/data5/suguru/test/sample_R3D.dv_decon'
        self.pattern = re.compile('^(.*)R3D\.dv$')

    def test_search_files(self):
        ignore_str = '|'.join([r'.*/\..*', '/data5/suguru/omero-imports'])
        ignore_pattern = re.compile(ignore_str)
        for dpath, fname in search_files('/data5/suguru/', self.pattern, ignore_pattern):
            fullpath = os.path.join(dpath,fname)
            self.assertEqual(fname[-6:], 'R3D.dv')
            self.assertEqual(ignore_pattern.match(dpath), None)
            print >> sys.stderr, fullpath

    def test_get_owner(self):
        owner = get_owner(self.dirpath)
        self.assertEqual(owner, 'suguru')
        owner = get_owner(self.deconpath)
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
                'path': self.deconpath
                }
        connected = connect(**kwargs)
        self.assertTrue('conn' in connected)
        self.assertNotEqual(connected['conn'], None)
        self.assertTrue(connected['conn'].isConnected())
        close_session(**connected)

    def test_init_chromatic_shift(self):
        kwargs = init_chromatic_shift(path=self.deconpath)
        self.assertTrue('zs' in kwargs)

    def test_check_not_imported_yet(self):
        kwargs = {
                'uname': 'suguru',
                'passwd': 'omx',
                'path': self.deconpath,
                'dirname': self.dirpath
                }
        connected = init_chromatic_shift(**connect(**kwargs))
        with self.assertRaises(EnvironmentError) as cm:
            check_not_imported_yet(**connected)

    def test_get_log(self):
        kwargs = init_chromatic_shift(path=self.deconpath)
        with self.assertRaises(ValueError):
            get_log(path=self.dirpath)
        try:
            logpath = get_log(**kwargs)['logfile']
        except IOError, err:
            self.fail(err)
        self.assertTrue(os.path.exists(logpath))

    def test_succeed(self):
        succeeded = succeed(path=self.deconpath)
        self.assertTrue('retval' in succeeded)
        self.assertTrue('SUCCESS' in succeeded['retval'])
        self.assertTrue(succeeded['retval']['SUCCESS'])
        self.assertTrue('path' in succeeded)
        self.assertEqual(succeeded['path'], self.deconpath)

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
        self.assertEqual(result[0]['ERROR']['ERRNO'], errno.EEXIST)

if __name__ == '__main__':
    unittest.main()
