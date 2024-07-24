#!/usr/bin/env python

import zarrita
from skimage.data import astronaut

# choose chunks s.t. we do have overhanging edge-chunks
CHUNK_SHAPE = (100, 100, 1)
SHARD_SHAPE = (1000, 1000, 3)
STR_TO_CODEC = {
    "gzip": zarrita.codecs.gzip_codec(),
    "blosc": zarrita.codecs.blosc_codec(cname="lz4", typesize=10),
}


def generate_zr3_format(list_only:bool, codecs=["gzip", "blosc", None], nested=True, sharded=True):
    im = astronaut()
    fname = "zarrita"
    if nested:
        chunk_separator = "/"
        fname += "_nested"
    else:
        chunk_separator = "."
    if sharded:
        fname += "_sharded"

    path = f"../../data/{fname}"
    store = zarrita.LocalStore(path)
    g = zarrita.Group.create(store, exists_ok=True)
    for codec in codecs:
        if codec is None:
            name = "raw"
        elif codec == "blosc":
            name = f"{codec}/{STR_TO_CODEC[codec].configuration.cname}"
        else:
            name = codec

        codecs_impl = [zarrita.codecs.bytes_codec()]
        if codec is not None:
            codecs_impl.append(STR_TO_CODEC[codec])

        if sharded:
            codecs_impl = [
                zarrita.codecs.sharding_codec(
                    chunk_shape=CHUNK_SHAPE, codecs=codecs_impl
                ),
            ]

        if list_only:
            print(f"{path}\t{name}")
        else:
            a = g.create_array(
                name,
                shape=im.shape,
                chunk_shape=SHARD_SHAPE if sharded else CHUNK_SHAPE,
                chunk_key_encoding=("default", chunk_separator),
                dtype=im.dtype,
                codecs=codecs_impl,
                exists_ok=True,
            )
            a[:, :, :]= im


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-list", action="store_true")
    parser.add_argument("-verify", action="store_true")
    parser.add_argument("args", nargs="*")
    ns = parser.parse_args()
    if ns.verify:
        verify_format(*ns.args)
    else:
        for nested in [False, True]:
            for sharded in [False, True]:
                generate_zr3_format(ns.list, nested=nested, sharded=sharded)
