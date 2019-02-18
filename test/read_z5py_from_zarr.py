import unittest
import numpy as np
import z5py
from skimage.data import astronaut


class TestReadZ5pyFromZarr(unittest.TestCase):
    im = astronaut()

    def test_read_zarr_format(self):
        path = '../data/zarr.zr'
        f = z5py.File(path)
        compressors = ('raw', 'blosc', 'zlib', 'gzip')
        for compressor in compressors:
            ds = f[compressor]
            data = ds[:]
            self.assertEqual(self.im.shape, data.shape)
            self.assertTrue(np.allclose(self.im, data))

    # NOTE this currently fails because zarr-n5 does not cut off
    # overhanging edge chunks
    def test_read_n5_format(self):
        path = '../data/zarr.n5'
        f = z5py.File(path)
        compressors = ('raw', 'gzip')
        for compressor in compressors:
            ds = f[compressor]
            data = ds[:]
            self.assertEqual(self.im.shape, data.shape)
            print(np.isclose(self.im, data).sum(), "/", data.size)
            self.assertTrue(np.allclose(self.im, data))


if __name__ == '__main__':
    unittest.main()
