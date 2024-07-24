#!/usr/bin/env python

import z5py
from skimage.data import astronaut

# choose chunks s.t. we do have overhanging edge-chunks
CHUNKS = (100, 100, 1)

# options for the different compressors
COMPRESSION_OPTIONS = {"blosc": {"codec": "lz4"}}


# TODO support more compressors:
# - more compressors in numcodecs
# - more blosc codecs
def generate_zarr_format(list_only:bool, compressors=['gzip', 'blosc', 'zlib', 'raw']):
    path = '../../data/z5py.zr'
    im = astronaut()

    f = z5py.File(path, mode='w')
    for compressor in compressors:
        copts = COMPRESSION_OPTIONS.get(compressor, {})
        name = (
            compressor
            if compressor != "blosc"
            else "%s/%s" % (compressor, copts.get("codec"))
        )
        if list_only:
            print(f"{path}\t{name}")
        else:
            f.create_dataset(name, data=im, compression=compressor, chunks=CHUNKS, **copts)


def generate_n5_format(list_only:bool, compressors=['gzip', 'raw']):
    path = '../../data/z5py.n5'
    im = astronaut()

    f = z5py.File(path, mode='w')
    for compressor in compressors:
        name = compressor
        if list_only:
            print(f"{path}\t{name}")
        else:
            f.create_dataset(name, data=im, chunks=CHUNKS, compression=compressor)


def verify_format(directory: str, dataset: str):
    f = z5py.File(f"{directory}/{dataset}", mode="r")
    return f[:]


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-list", action="store_true")
    parser.add_argument("-verify", action="store_true")
    parser.add_argument("args", nargs="*")
    ns = parser.parse_args()
    if ns.verify:
        verify_format(*ns.args)
    else:
        generate_zarr_format(ns.list)
        generate_n5_format(ns.list)
