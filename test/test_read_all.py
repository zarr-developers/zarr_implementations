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
    if nested:
        store = zarr.storage.FSStore(
            os.fspath(fpath), key_separator='/', mode='r'
        )
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


def create_params():
    argnames = ["fmt", "writing_library", "reading_library", "codec", "nested"]
    params = []
    ids = []
    for fmt in EXTENSIONS:
        for file_stem, fpath in libraries_for_format(fmt).items():
            nested = "_nested" in file_stem
            writing_library = file_stem.replace("_nested", "")
            nested_str = "nested" if nested else ""
            written_codecs = codecs_for_file(fpath)
            for reading_library, available_fmts in READABLE_CODECS.items():
                available_codecs = available_fmts.get(fmt, [])
                for codec in sorted(
                    set(available_codecs).intersection(written_codecs)
                ):
                    params.append(
                        (fmt, writing_library, reading_library, codec, nested)
                    )
                    ids.append(
                        f"read {nested_str} {writing_library} {fmt} using "
                        f"{reading_library}, {codec}"
                    )
    return argnames, params, ids


argnames, params, ids = create_params()


def _get_read_fn(fmt, writing_library, reading_library):
    fpath = DATA_DIR / f"{writing_library}{EXTENSIONS[fmt]}"
    read_fn = {
        "zarr": read_with_zarr,
        "pyn5": read_with_pyn5,
        "z5py": read_with_z5py,
        "zarrita": read_with_zarrita,
    }[reading_library]
    return fpath, read_fn


@pytest.mark.parametrize(argnames, params, ids=ids)
def test_correct_read(fmt, writing_library, reading_library, codec, nested):
    if nested and reading_library != 'zarr':
        pytest.skip("nested read not implemented")

    reference = imread(DATA_DIR / "reference_image.png")
    nested_str = "_nested" if nested else ""
    fpath, read_fn = _get_read_fn(fmt, writing_library, reading_library)
    test = read_fn(fpath, codec, nested)
    assert test.shape == reference.shape
    assert np.allclose(test, reference)


def tabulate_test_results(params, per_codec_tables=False):
    reference = imread(DATA_DIR / "reference_image.png")

    all_results = {}
    for fmt, writing_library, reading_library, codec in params:
        fpath, read_fn = _get_read_fn(fmt, writing_library, reading_library)
        fail_type = None
        try:
            test = read_fn(fpath, codec)
        except Exception as e:
            fail_type = f"{type(e).__name__}: {e}"

        if fail_type is None:
            result = test.shape == reference.shape
            result = result and np.allclose(test, reference)
        else:
            result = fail_type

        if per_codec_tables:
            table_key = fmt, codec
            inner_key = (writing_library, reading_library)
        else:
            table_key = fmt
            inner_key = (', '.join((writing_library, codec)), reading_library)

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
        df.at[k[0], k[1]] = df_val\

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
