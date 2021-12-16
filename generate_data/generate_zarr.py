import zarr
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


# TODO use more compressors from numcodecs and more blosc filter_ids
def generate_zarr_format(compressors=['gzip', 'blosc', 'zlib', None]):

    for nested, StoreClass, store_kwargs in [
        # zarr version 2 flat storage cases
        (False, zarr.storage.DirectoryStore, {}),
        (False, zarr.storage.FSStore, {}),
        # zarr version 2 nested storage cases
        (True, zarr.storage.NestedDirectoryStore, {}),
        (True, zarr.storage.FSStore,
         {'dimension_separator': '/', 'auto_mkdir': True}),
        # zarr version 3 flat storage cases
        (False, zarr.storage.DirectoryStoreV3, {'dimension_separator': '.'}),
        (False, zarr.storage.FSStoreV3, {'dimension_separator': '.'}),
        # zarr version 3 nested storage cases
        (True, zarr.storage.DirectoryStoreV3, {}),
        (True, zarr.storage.FSStoreV3, {}),
    ]:

        nested_str = '_nested' if nested else '_flat'
        path = f'data/zarr_{StoreClass.__name__}{nested_str}.zr'
        store = StoreClass(path, **store_kwargs)
        im = astronaut()

        zarr_version = StoreClass._store_version
        # must specify a top-level group path for zarr.open when using zarr-v3
        path = None if zarr_version == 2 else 'astronaut'

        f = zarr.open(store, path=path, mode='w')
        for compressor in compressors:
            copts = COMPRESSION_OPTIONS.get(compressor, {})
            if compressor is None:
                name = "raw"
            elif compressor == "blosc":
                name = "%s/%s" % (compressor, copts.get("cname"))
            else:
                name = compressor
            compressor_impl = STR_TO_COMPRESSOR[compressor](**copts) if compressor is not None else None
            f.create_dataset(name, data=im, chunks=CHUNKS,
                             compressor=compressor_impl)


def generate_n5_format(compressors=['gzip', None]):
    im = astronaut()

    f = zarr.open('data/zarr.n5', mode='w')
    for compressor in compressors:
        name = compressor if compressor is not None else 'raw'
        compressor_impl = STR_TO_COMPRESSOR[compressor]() if compressor is not None else None
        f.create_dataset(name, data=im, chunks=CHUNKS,
                         compressor=compressor_impl)




if __name__ == '__main__':
    generate_zarr_format()
    generate_n5_format()
