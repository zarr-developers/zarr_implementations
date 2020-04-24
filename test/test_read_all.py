"""
Usage
=====

When a new library, format, or codec is added, update

* READABLE_CODECS.{library_name}.{format_name}[{codec1}, {codec2}, ...]
* Write a function which takes a container path and dataset name,
  and returns a numpy-esque array
* Add it to READ_FNS under the {library_name} key

The matrix of tests is automatically generated,
and individual tests correctly fail on unavailable imports.
Call ``pytest`` in the root directory to run all of the tests.
"""
import os
from typing import Dict, List
from pathlib import Path
from skimage.io import imread

import numpy as np
import pytest


READABLE_CODECS: Dict[str, Dict[str, List[str]]] = {
    "z5py": {
        "zarr": ["blosc", "gzip", "raw", "zlib"],
        "N5": ["gzip", "raw"],
    },
    "pyn5": {
        "N5": ["bzip2", "gzip", "raw"],
        "zarr": [],
    },
    "zarr": {
        "zarr": ["blosc", "gzip", "raw", "zlib"],
        "N5": ["gzip", "raw"],
    }
}


def read_with_zarr(fpath, ds_name):
    import zarr
    return zarr.open(os.fspath(fpath))[ds_name][:]


def read_with_pyn5(fpath, ds_name):
    import pyn5
    return pyn5.File(fpath)[ds_name][:]


def read_with_z5py(fpath, ds_name):
    import z5py
    return z5py.File(fpath)[ds_name][:]


READ_FNS = {
    "zarr": read_with_zarr,
    "pyn5": read_with_pyn5,
    "z5py": read_with_z5py,
}


EXTENSIONS = {"zarr": ".zr", "N5": ".n5"}
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"


def libraries_for_format(format: str):
    return {
        fpath.stem: fpath
        for fpath in sorted(DATA_DIR.glob(f"*{EXTENSIONS[format]}"))
    }


def codecs_for_file(fpath: Path):
    return sorted(d.name for d in fpath.iterdir() if d.is_dir())


def create_params():
    argnames = ["fmt", "writing_library", "reading_library", "codec"]
    params = []
    ids = []
    for fmt in EXTENSIONS:
        for writing_library, fpath in libraries_for_format(fmt).items():
            written_codecs = codecs_for_file(fpath)
            for reading_library, available_fmts in READABLE_CODECS.items():
                available_codecs = available_fmts.get(fmt, [])
                for codec in sorted(
                    set(available_codecs).intersection(written_codecs)
                ):
                    params.append(
                        (fmt, writing_library, reading_library, codec)
                    )
                    ids.append(
                        f"read {writing_library} {fmt} using "
                        f"{reading_library}, {codec}"
                    )
    return argnames, params, ids


argnames, params, ids = create_params()
print(params)


@pytest.mark.parametrize(argnames, params, ids=ids)
def test_correct_read(fmt, writing_library, reading_library, codec):
    reference = imread(DATA_DIR / "reference_image.png")
    fpath = DATA_DIR / f"{writing_library}{EXTENSIONS[fmt]}"
    read_fn = {
        "zarr": read_with_zarr,
        "pyn5": read_with_pyn5,
        "z5py": read_with_z5py,
    }[reading_library]
    test = read_fn(fpath, codec)
    assert test.shape == reference.shape
    assert np.allclose(test, reference)
