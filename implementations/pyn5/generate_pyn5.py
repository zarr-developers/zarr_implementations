#!/usr/bin/env python
from pathlib import Path
import pyn5
from skimage.io import imread

# choose chunks s.t. we do have overhanging edge-chunks
CHUNKS = (100, 100, 1)


def generate_n5_format(compressors=pyn5.CompressionType):
    here = Path(__file__).resolve().parent
    data_dir = here.parent.parent / "data"
    path = data_dir / "pyn5.n5"

    im = imread(data_dir / "reference_image.png")

    f = pyn5.File(path, pyn5.Mode.CREATE_TRUNCATE)
    for compressor in compressors:
        name = str(compressor)
        f.create_dataset(name, data=im, chunks=CHUNKS, compression=compressor)


if __name__ == '__main__':
    generate_n5_format()
