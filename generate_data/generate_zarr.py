import zarr
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
def generate_zarr_format(compressors=['gzip', 'blosc', 'zlib', None],
                         nested=False):
    if nested:
        path = 'data/zarr.zr'
        store = path
    else:
        path = 'data/zarr_nested.zr'
        store = zarr.storage.FSStore(path, key_separator='/', auto_mkdir=True)
    im = astronaut()

    f = zarr.open(store, mode='w')
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
    im = astronaut()

    f = zarr.open('data/zarr.n5', mode='w')
    for compressor in compressors:
        name = compressor if compressor is not None else 'raw'
        compressor_impl = STR_TO_COMPRESSOR[compressor]() if compressor is not None else None
        f.create_dataset(name, data=im, chunks=CHUNKS,
                         compressor=compressor_impl)


if __name__ == '__main__':
    for nested in [False, True]:
        generate_zarr_format(nested=nested)
    generate_n5_format()
