#!/usr/bin/env python

import tensorstore as ts
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

im = astronaut()
SIZE = im.shape


def n5_metadata(compression: str):
    return {
        'compression': {
            'type': compression,
        },
        'dataType': 'uint32',
        'dimensions': SIZE,
        'blockSize': CHUNKS,
    }

def zr_metadata():
    if True:
        chunk_grid = {"name": "regular", "configuration": {"chunk_shape": chunks}}  # read size

        sharding_codec = {
            "name": "sharding_indexed",
            "configuration": {
                "chunk_shape": chunks, # write size
                "codecs": [{"name": "bytes", "configuration": {"endian": "little"}},
                           {"name": "blosc", "configuration": {"cname": "zstd", "clevel": 5}}],
                "index_codecs": [{"name": "bytes", "configuration": {"endian": "little"}},
                                 {"name": "crc32c"}],
                "index_location": "end"
            }
        }
        codecs = [sharding_codec]
    else:
        # Alternative without sharding...
        chunk_grid = {"name": "regular", "configuration": {"chunk_shape": chunks}}
        blosc_codec = {"name": "blosc", "configuration": { "cname": "lz4", "clevel": 5}}
        codecs = [blosc_codec]

    base_config = {
        "driver": "zarr3",
        "kvstore": CONFIGS[1],
        "metadata": {
            "shape": shape,
            "chunk_grid": chunk_grid,
            "chunk_key_encoding": {"name": "default"}, # "configuration": {"separator": "/"}},
            "codecs": codecs,
            "data_type": read.dtype,
            "dimension_names": dimension_names,
        }
    }


def ts_write(driver: str, path: str, metadata: dict, data: List):
    arr = ts.open({
        'driver': driver,
        'kvstore': {
            'driver': 'file',
            'path': path,
        },
        'metadata': metadata,
        'create': True,
        'delete_existing': True,
    }).result()
    write_future = arr.write(data)
    write_future.result()


# TODO use more compressors from numcodecs and more blosc filter_ids
def generate_zarr_format(list_only:bool, compressors=['gzip', 'blosc', 'zlib', None]):
    for compressor in compressors:
        copts = COMPRESSION_OPTIONS.get(compressor, {})
        if compressor is None:
            name = "raw"
        elif compressor == "blosc":
            name = "%s/%s" % (compressor, copts.get("cname"))
        else:
            name = compressor
        compressor_impl = STR_TO_COMPRESSOR[compressor](**copts) if compressor is not None else None
        # V2. TODO: add method for v3 everywhere
        if list_only:
            print(f"data/tensorstore.zr\t{name}")
        else:
            ts_write('zarr', f'data/tensorstore.zr/{name}', zr_metadata(), im)


def generate_n5_format(list_only:bool, compressors=['gzip', None]):
    im = astronaut()
    for compressor in compressors:
        name = compressor if compressor is not None else 'raw'
        compressor_impl = STR_TO_COMPRESSOR[compressor]() if compressor is not None else None
        if list_only:
            print(f"data/tensorstore.n5\t{name}")
        else:
            ts_write('zarr', f'data/tensorstore.n5/{name}', n5_metadata(), im)


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
