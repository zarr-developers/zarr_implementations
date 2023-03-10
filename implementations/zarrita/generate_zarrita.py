import zarrita
from skimage.data import astronaut

# choose chunks s.t. we do have overhanging edge-chunks
CHUNK_SHAPE = (100, 100, 1)
SHARD_SHAPE = (1000, 1000, 3)
STR_TO_CODEC = {
    "gzip": zarrita.codecs.gzip_codec(),
    "blosc": zarrita.codecs.blosc_codec(cname="lz4"),
}


def generate_zr3_format(codecs=["gzip", "blosc", None], nested=True, sharded=True):
    im = astronaut()
    fname = "zarrita"
    if nested:
        chunk_separator = "/"
        fname += "_nested"
    else:
        chunk_separator = "."
    if sharded:
        fname += "_sharded"
    store = zarrita.FileSystemStore("file://./data")
    g = zarrita.Group.create(store, fname)
    for codec in codecs:
        if codec is None:
            name = "raw"
        elif codec == "blosc":
            name = f"{codec}/{STR_TO_CODEC[codec].configuration.cname}"
        else:
            name = codec
        codecs_impl = [STR_TO_CODEC[codec]] if codec is not None else []
        if sharded:
            codecs_impl = [
                zarrita.codecs.sharding_codec(
                    chunk_shape=CHUNK_SHAPE, codecs=codecs_impl
                )
            ]
        a = g.create_array(
            name,
            shape=im.shape,
            chunk_shape=SHARD_SHAPE if sharded else CHUNK_SHAPE,
            chunk_key_encoding=("default", chunk_separator),
            dtype=im.dtype,
            codecs=codecs_impl,
        )
        a[...] = im


if __name__ == "__main__":
    for nested in [False, True]:
        for sharded in [False, True]:
            generate_zr3_format(nested=nested, sharded=sharded)
