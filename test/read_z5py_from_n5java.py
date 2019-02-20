import unittest
import numpy as np
import z5py
from skimage.data import astronaut


class TestReadZ5pyFromZarr(unittest.TestCase):
    im = astronaut()

    def test_read_n5_format(self):
        path = '../data/n5-java.n5'
        f = z5py.File(path)
        # TODO check more compression
        compressors = ('raw', 'gzip')
        for compressor in compressors:
            ds = f[compressor]
            data = ds[:]
            self.assertEqual(self.im.shape, data.shape)
            self.assertTrue(np.allclose(self.im, data))


if __name__ == '__main__':
    unittest.main()
