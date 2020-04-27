import z5py
from skimage.data import astronaut

# choose chunks s.t. we do have overhanging edge-chunks
CHUNKS = (100, 100, 1)


def generate_zarr_format(compressors=['gzip', 'blosc', 'zlib', 'raw']):
    path = '../data/z5py.zr'
    im = astronaut()

    f = z5py.File(path)
    for compressor in compressors:
        name = compressor
        f.create_dataset(name, data=im, compression=compressor, chunks=CHUNKS)


def generate_n5_format(compressors=['gzip', 'raw']):
    path = '../data/z5py.n5'
    im = astronaut()

    f = z5py.File(path, mode='w')
    for compressor in compressors:
        name = compressor
        f.create_dataset(name, data=im, chunks=CHUNKS, compression=compressor)


if __name__ == '__main__':
    generate_zarr_format()
    generate_n5_format()
