import zarr
import numcodecs
from skimage.data import astronaut

# choose chunks s.t. we do have overhanging edge-chunks
CHUNKS = (100, 100, 1)
STR_TO_COMPRESSOR = {'gzip': numcodecs.GZip(),
                     'blosc': numcodecs.Blosc(),
                     'zlib': numcodecs.Zlib()}


def generate_zarr_format(compressors=['gzip', 'blosc', 'zlib', None]):
    path = '../data/zarr.zr'
    im = astronaut()

    f = zarr.open(path)
    for compressor in compressors:
        name = compressor if compressor is not None else 'raw'
        compressor_impl = STR_TO_COMPRESSOR[compressor] if compressor is not None else None
        f.create_dataset(name, data=im, chunks=CHUNKS,
                         compressor=compressor_impl)


# this needs PR https://github.com/zarr-developers/zarr/pull/309
def generate_n5_format(compressors=['gzip', None]):
    path = '../data/zarr.n5'
    im = astronaut()

    f = zarr.open(path)
    for compressor in compressors:
        name = compressor if compressor is not None else 'raw'
        compressor_impl = STR_TO_COMPRESSOR[compressor] if compressor is not None else None
        f.create_dataset(name, data=im, chunks=CHUNKS,
                         compressor=compressor_impl)


if __name__ == '__main__':
    generate_zarr_format()
    generate_n5_format()
