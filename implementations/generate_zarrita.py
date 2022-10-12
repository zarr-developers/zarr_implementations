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


def generate_zr3_format(compressors=['gzip', 'blosc', 'zlib', None],
                        nested=True):
    im = astronaut()
    if nested:
        chunk_separator = '/'
        fname = 'data/zarrita_nested.zr3'
    else:
        chunk_separator = '.'
        fname = 'data/zarrita.zr3'
    h = zarrita.create_hierarchy(fname)
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
                           chunk_separator=chunk_separator, dtype=im.dtype,
                           compressor=compressor_impl)
        a[...] = im


if __name__ == '__main__':
    for nested in [False, True]:
        generate_zr3_format(nested=nested)
