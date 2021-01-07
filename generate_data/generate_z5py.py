import z5py
from skimage.data import astronaut

# choose chunks s.t. we do have overhanging edge-chunks
CHUNKS = (100, 100, 1)

# options for the different compressors
COMPRESSION_OPTIONS = {"blosc": {"codec": "lz4"}}


# TODO support more compressors:
# - more compressors in numcodecs
# - more blosc codecs
def generate_zarr_format(compressors=['gzip', 'blosc', 'zlib', 'raw']):
    path = 'data/z5py.zr'
    im = astronaut()

    f = z5py.File(path)
    for compressor in compressors:
        copts = COMPRESSION_OPTIONS.get(compressor, {})
        name = (
            compressor
            if compressor != "blosc"
            else "%s/%s" % (compressor, copts.get("codec"))
        )
        f.create_dataset(name, data=im, compression=compressor, chunks=CHUNKS, **copts)


def generate_n5_format(compressors=['gzip', 'raw']):
    path = 'data/z5py.n5'
    im = astronaut()

    f = z5py.File(path)
    for compressor in compressors:
        name = compressor
        f.create_dataset(name, data=im, chunks=CHUNKS, compression=compressor)


if __name__ == '__main__':
    generate_zarr_format()
    generate_n5_format()
