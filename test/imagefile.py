# -*- coding: utf-8 -*-
import unittest
from src import ImageFile

class TestImageFile(unittest.TestCase):

    def setUp(self):
        self.decon_zs = ImageFile('/data2/gkafer/Exp49/2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv_decon.zs')
        self.d3d_zs = ImageFile('2013_4_10_Kafer_Exp49_Slide1a01_R3D_D3D.dv.zs')
        self.decon = ImageFile('2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv_decon')

    def test_is_shifted(self):
        self.assertTrue(self.decon_zs.is_shifted)
        self.assertTrue(self.d3d_zs.is_shifted)
        self.assertFalse(self.decon.is_shifted)

    def test_is_deconvoluted(self):
        self.assertTrue(self.decon_zs.is_deconvoluted)
        self.assertTrue(self.d3d_zs.is_deconvoluted)
        self.assertTrue(self.decon.is_deconvoluted)

    def test_get_basename(self):
        self.assertEqual(self.decon_zs.basename,
                '2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv_decon.zs')
        self.assertEqual(self.d3d_zs.basename,
                '2013_4_10_Kafer_Exp49_Slide1a01_R3D_D3D.dv.zs')
        self.assertEqual(self.decon.basename,
                '2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv_decon')

    def test_get_origin_name(self):
        self.assertEqual(self.decon_zs.origin_name,
                '2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv')
        self.assertEqual(self.d3d_zs.origin_name,
                '2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv')
        self.assertEqual(self.decon.origin_name,
                '2013_4_10_Kafer_Exp49_Slide1a01_R3D.dv')

if __name__ == '__main__':
    unittest.main()
