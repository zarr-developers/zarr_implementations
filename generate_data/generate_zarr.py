import zarr
import zarrita
import numcodecs
from skimage.data import astronaut

# choose chunks s.t. we do have overhanging edge-chunks
CHUNKS = (100, 100, 1)
STR_TO_COMPRESSOR = {
    "gzip": numcodecs.GZip,
    "blosc": numcodecs.Blosc,
    "zlib": numcodecs.Zlib,
}
COMPRESSION_OPTIONS = {"blosc": {"cname": "lz4"}}


# TODO use more compressors from numcodecs and more blosc filter_ids
def generate_zarr_format(compressors=['gzip', 'blosc', 'zlib', None]):
    path = 'data/zarr.zr'
    im = astronaut()

    f = zarr.open(path, mode='w')
    for compressor in compressors:
        copts = COMPRESSION_OPTIONS.get(compressor, {})
        if compressor is None:
            name = "raw"
        elif compressor == "blosc":
            name = "%s/%s" % (compressor, copts.get("cname"))
        else:
            name = compressor
        compressor_impl = STR_TO_COMPRESSOR[compressor](**copts) if compressor is not None else None
        f.create_dataset(name, data=im, chunks=CHUNKS,
                         compressor=compressor_impl)


def generate_n5_format(compressors=['gzip', None]):
    path = 'data/zarr.n5'
    im = astronaut()

    f = zarr.open(path, mode='w')
    for compressor in compressors:
        name = compressor if compressor is not None else 'raw'
        compressor_impl = STR_TO_COMPRESSOR[compressor]() if compressor is not None else None
        f.create_dataset(name, data=im, chunks=CHUNKS,
                         compressor=compressor_impl)


def generate_zr3_format(compressors=['gzip', 'blosc', 'zlib', None]):
    im = astronaut()

    h = zarrita.create_hierarchy('data/zarr.zr3')
    for compressor in compressors:
        copts = COMPRESSION_OPTIONS.get(compressor, {})
        if compressor is None:
            name = "raw"
        elif compressor == "blosc":
            name = "%s/%s" % (compressor, copts.get("cname"))
        else:
            name = compressor
        compressor_impl = STR_TO_COMPRESSOR[compressor](**copts) if compressor is not None else None
        a = h.create_array('/' + name, shape=im.shape, chunk_shape=CHUNKS,
                           dtype=im.dtype, compressor=compressor_impl)
        a[...] = im


if __name__ == '__main__':
    generate_zarr_format()
    generate_n5_format()
    generate_zr3_format()
