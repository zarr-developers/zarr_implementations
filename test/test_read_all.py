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

The tests in this folder assume that the data generation scripts generate
filenames named as follows:

{writing_library}.{fmt}

where {fmt} is '.n5', '.zr' or '.zr3'.

For writers where multiple store and/or file nesting formats are tested, the
following filenaming scheme is used in the generators:

{writing_library}_{storage_class_name}_{nesting_type}.{fmt}

'_{storage_class_name}' is optional and is currently used by the zarr-python
implementations to indicate which storage class was used to write the data.

'_{nesting_type}' should be either '_nested' or '_flat' to indicate if a
nested or flat chunk storage scheme is used.

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
        "zarr-v3": [],
        "N5": ["gzip", "raw"],
    },
    "pyn5": {
        "N5": ["bzip2", "gzip", "raw"],
        "zarr-v3": [],
        "zarr": [],
    },
    "zarr": {
        "zarr": ["blosc", "gzip", "raw", "zlib"],
        "zarr-v3": [],
        "N5": ["gzip", "raw"],
    },
    "zarrita": {
        "zarr": [],
        "zarr-v3": ["blosc", "gzip", "raw", "zlib"],
        "N5": [],
    }
}


def read_with_zarr(fpath, ds_name, nested):
    import zarr
    if ds_name == "blosc":
        ds_name = "blosc/lz4"
    if str(fpath).endswith('.zr'):
        if nested:
            if 'FSStore' in str(fpath):
                store = zarr.storage.FSStore(
                    os.fspath(fpath), key_separator='/', mode='r'
                )
            else:
                store = zarr.storage.NestedDirectoryStore(os.fspath(fpath))
        else:
            if 'FSStore' in str(fpath):
                store = zarr.storage.FSStore(os.fspath(fpath))
            else:
                store = zarr.storage.DirectoryStore(fpath)
    else:
        store = os.fspath(fpath)
    return zarr.open(store)[ds_name][:]


def read_with_pyn5(fpath, ds_name, nested):
    import pyn5
    return pyn5.File(fpath)[ds_name][:]


def read_with_z5py(fpath, ds_name, nested):
    import z5py
    if ds_name == "blosc":
        ds_name = "blosc/lz4"
    return z5py.File(fpath)[ds_name][:]


def read_with_zarrita(fpath, ds_name, nested):
    import zarrita
    if ds_name == "blosc":
        ds_name = "blosc/lz4"
    h = zarrita.get_hierarchy(str(fpath.absolute()))
    return h["/" + ds_name][:]


READ_FNS = {
    "zarr": read_with_zarr,
    "zarrita": read_with_zarrita,
    "pyn5": read_with_pyn5,
    "z5py": read_with_z5py,
}


EXTENSIONS = {"zarr": ".zr", "N5": ".n5", "zarr-v3": ".zr3"}
HERE = Path(__file__).resolve().parent
DATA_DIR = HERE.parent / "data"

# Optional filename strings indicating a specific storage class was used
KNOWN_STORAGE_CLASSES = {"DirectoryStore", "FSStore", "NestedDirectoryStore"}


def libraries_for_format(format: str):
    return {
        fpath.stem: fpath
        for fpath in sorted(DATA_DIR.glob(f"*{EXTENSIONS[format]}"))
    }


def codecs_for_file(fpath: Path):
    if fpath.name.endswith('.zr3'):
        # for zarr v3 have to search for the arrays in the data root folder
        data_root = fpath / 'data' / 'root'
        return sorted(d.name for d in data_root.iterdir() if d.is_dir())
    else:
        return sorted(d.name for d in fpath.iterdir() if d.is_dir())


def _get_write_attrs(file_stem: str):
    """Parse a filename to determine the writing library name

    If present in the filename, the storage class and nesting type are also
    determined.
    """
    nested_str = ""
    if "nested" in file_stem:
        nested_str = "nested"
        writing_library = file_stem.replace("_nested", "")
    else:
        writing_library = file_stem

    if "_flat" in file_stem:
        writing_library = file_stem.replace("_flat", "")

    store_str = ""
    for store_name in KNOWN_STORAGE_CLASSES:
        _store_name = '_' + store_name
        if _store_name in writing_library:
            if store_str:
                raise ValueError(
                    f"multiple store names in file_stem: {file_stem}"
                )
            store_str = store_name
            writing_library = writing_library.replace(_store_name, "")

    return writing_library, store_str, nested_str


def create_params():
    argnames = ["fmt", "writing_library", "reading_library", "codec", "nested",
                "store_name", "fpath"]
    params = []
    ids = []
    for fmt in EXTENSIONS:
        for file_stem, fpath in libraries_for_format(fmt).items():
            writing_library, store_str, nested_str = _get_write_attrs(file_stem)
            nested = nested_str == "nested"
            written_codecs = codecs_for_file(fpath)
            for reading_library, available_fmts in READABLE_CODECS.items():
                available_codecs = available_fmts.get(fmt, [])
                for codec in sorted(
                    set(available_codecs).intersection(written_codecs)
                ):
                    params.append(
                        (fmt, writing_library, reading_library, codec, nested,
                         store_str, fpath)
                    )
                    write_attrs = ', '.join(
                        [s for s in (store_str, nested_str) if s != ""]
                    )
                    if write_attrs:
                        write_attrs = ' (' + write_attrs + ')'
                    ids.append(
                        f"read {writing_library}{write_attrs} {fmt} using "
                        f"{reading_library}, {codec}"
                    )
    return argnames, params, ids


argnames, params, ids = create_params()


def _get_read_fn(reading_library):
    read_fn = {
        "zarr": read_with_zarr,
        "pyn5": read_with_pyn5,
        "z5py": read_with_z5py,
        "zarrita": read_with_zarrita,
    }[reading_library]
    return read_fn


@pytest.mark.parametrize(argnames, params, ids=ids)
def test_correct_read(fmt, writing_library, reading_library, codec, nested,
                      store_name, fpath):
    if nested and reading_library == 'z5py':
        pytest.skip("nested read not implemented in z5py")

    reference = imread(DATA_DIR / "reference_image.png")
    read_fn = _get_read_fn(reading_library)
    if not os.path.exists(fpath):
        raise RuntimeError(
            f"file not found: {fpath}. Make sure you have generated the data "
            "using 'make data'"
        )
    test = read_fn(fpath, codec, nested)
    assert test.shape == reference.shape
    assert np.allclose(test, reference)


def tabulate_test_results(params, per_codec_tables=False):
    reference = imread(DATA_DIR / "reference_image.png")

    all_results = {}
    for (fmt, writing_library, reading_library, codec, nested, store_name,
            fpath) in params:
        read_fn = _get_read_fn(reading_library)
        fail_type = None
        try:
            test = read_fn(fpath, codec, nested)
        except Exception as e:
            fail_type = f"{type(e).__name__}: {e}"

        if fail_type is None:
            result = test.shape == reference.shape
            result = result and np.allclose(test, reference)
        else:
            result = fail_type

        nstr = 'nested' if nested else 'flat'
        if per_codec_tables:
            table_key = fmt, codec
            inner_key = (', '.join(writing_library, store_name, nstr), reading_library)
        else:
            table_key = fmt
            if store_name:
                key_attributes = (writing_library, codec, store_name, nstr)
            else:
                key_attributes = (writing_library, codec, nstr)
            inner_key = (', '.join(key_attributes), reading_library)

        if table_key not in all_results:
            all_results[table_key] = {}

        all_results[table_key][inner_key] = result

    return all_results


def result_to_table(result, use_emojis=True, fmt='md'):
    """Generate a markdown style table

    Parmaters
    ---------
    result : dict
        Dict where the keys are a 2-tuple of strings indicating the
        (index, column) labels and the values are the value at that location.
    use_emojis : bool, optional
        If True, emoji checkmarks will be used within the table. Otherwise
        plain text entries (e.g. SUCCESS, FAILURE) are used instead.
    fmt : {'md', 'html'}
        'md' and 'html' give Markdown and HTML format outputs, respectively.

    Returns
    -------
    table : str
        str containing the table in Markdown format
    """
    import pandas as pd

    # e.g res = all_results[('zarr', 'raw')]
    df = pd.DataFrame()
    writers = sorted(list(set([k[0] for k in result.keys()])))
    readers = sorted(list(set([k[1] for k in result.keys()])))
    df = pd.DataFrame(index=writers, columns=readers, dtype=str)
    df[:] = '----'
    if fmt == 'md':
        fail_str = ':x:' if use_emojis else 'FAILED'
        pass_str = ':heavy_check_mark:' if use_emojis else 'PASSED'
    elif fmt == 'html':
        fail_str = '&#10060;'  # HTML code for cross mark
        pass_str = '&#10004;'  # HTML code for heavy check mark
    else:
        fail_str = 'FAILED'
        pass_str = 'PASSED'

    for k, v in result.items():
        # df[k[1]][k[0]] = f"{v}"
        if v not in [True, False]:
            df_val = fail_str + f": {v}"
        else:
            if use_emojis:
                df_val = pass_str if v else f'{fail_str}: mismatched'
            else:
                df_val = pass_str if v else fail_str
        df.at[k[0], k[1]] = df_val

    if fmt == 'html':
        table = df.to_html()
        # undo any replacements of & with &amp;
        return table.replace(r'&amp;', '&')
    else:
        return df.to_markdown()


def concatenate_tables(all_results, use_emojis=True, fmt='md'):
    """Generate a report containing markdown-style tables

    Parmaters
    ---------
    all_results : dict
        Dict of test results as returned by generate_report
    use_emojis : bool, optional
        If True, emoji checkmarks will be used within the table. Otherwise
        plain text entries (e.g. SUCCESS, FAILURE) are used instead.
    fmt : {'md', 'html'}
        'md' and 'html' give Markdown and HTML format outputs, respectively.

    Returns
    -------
    report : str
        str containing the report in Markdown format
    """
    if fmt == 'html':
        header = """
            <!DOCTYPE html>
            <html>
            <head>
            <meta charset="UTF-8">\n\n
        """
        report = '\n'.join(h.lstrip(' ') for h in header.split('\n'))


        for table_name, res in all_results.items():
            report += f'<p><h1>{table_name}</h1></p>\n'
            report += result_to_table(res, use_emojis=use_emojis, fmt=fmt)
            report += '<br><br>\n\n\n'

        footer = """
            </head>
            <body>
        """
        report += '\n'.join(f.lstrip(' ') for f in footer.split('\n'))

    elif fmt == 'md':
        report = ''
        for table_name, res in all_results.items():
            report += f'# {table_name} Results\n'
            report += result_to_table(res, use_emojis=use_emojis, fmt=fmt)
            report += '\n\n\n'
    else:
        raise ValueError(f"unkown fmt: '{fmt}'. Must be 'md' or 'html'")

    return report


if __name__ == '__main__':


    all_results = tabulate_test_results(params)

    # save version with checkmark emojis to disk
    report_md = concatenate_tables(all_results, use_emojis=True, fmt='md')
    with open('report.md', 'wt') as f:
        f.writelines(report_md)

    # save HTML version to disk
    report_html = concatenate_tables(all_results, fmt='html')
    with open('report.html', 'wt') as f:
        f.writelines(report_html)

    # print version with plain text entries to the console
    print(concatenate_tables(all_results, use_emojis=False, fmt='md'))
