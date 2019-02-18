import unittest
import numpy as np
import zarr
from skimage.data import astronaut


class TestReadZarrFromZ5py(unittest.TestCase):
    im = astronaut()

    def test_read_zarr_format(self):
        path = '../data/z5py.zr'
        f = zarr.open(path)
        compressors = ('gzip', 'blosc', 'zlib', 'raw')
        for compressor in compressors:
            ds = f[compressor]
            data = ds[:]
            self.assertEqual(self.im.shape, data.shape)
            self.assertTrue(np.allclose(self.im, data))

    def test_read_n5_format(self):
        path = '../data/z5py.n5'
        f = zarr.open(path)
        compressors = ('gzip', 'raw')
        for compressor in compressors:
            ds = f[compressor]
            data = ds[:]
            self.assertEqual(self.im.shape, data.shape)
            self.assertTrue(np.allclose(self.im, data))


if __name__ == '__main__':
    unittest.main()
