#!/usr/bin/env python
from pathlib import Path
import pyn5
from skimage.io import imread

# choose chunks s.t. we do have overhanging edge-chunks
CHUNKS = (100, 100, 1)


def generate_n5_format(list_only: bool, compressors=pyn5.CompressionType):
    data_dir = Path("../..") / "data"
    path = data_dir / "pyn5.n5"

    im = imread(data_dir / "reference_image.png")

    f = pyn5.File(path, pyn5.Mode.CREATE_TRUNCATE)
    for compressor in compressors:
        name = str(compressor)
        if list_only:
            print(f"{path}\t{name}")
        else:
            f.create_dataset(name, data=im, chunks=CHUNKS, compression=compressor)


def verify_format(directory: str, dataset: str):
    f = pyn5.File(f"{directory}/{dataset}")# TODO, mode="r")
    return f[:]


if __name__ == '__main__':
    import sys
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("-list", action="store_true")
    parser.add_argument("-verify", action="store_true")
    parser.add_argument("args", nargs="*")
    ns = parser.parse_args()
    if ns.verify:
        verify_format(*ns.args)
    else:
        generate_n5_format(ns.list)
