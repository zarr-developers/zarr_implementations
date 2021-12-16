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
        zarr_version = StoreClass._store_version
        if zarr_version == 3:
            path = path.replace('.zr', '.zr3')
        store = StoreClass(path, **store_kwargs)
        im = astronaut()

        if zarr_version == 2:
            # can't open a group without an explicit `path` on v3
            f = zarr.open(store, mode='w')
        for compressor in compressors:
            copts = COMPRESSION_OPTIONS.get(compressor, {})
            if compressor is None:
                name = "raw"
            elif compressor == "blosc":
                name = "%s/%s" % (compressor, copts.get("cname"))
            else:
                name = compressor
            compressor_impl = STR_TO_COMPRESSOR[compressor](**copts) if compressor is not None else None
            if zarr_version == 2:
                f.create_dataset(name, data=im, chunks=CHUNKS,
                                 compressor=compressor_impl)
            else:
                # Note: dimension_separator will be inferred from store
                x = zarr.open_array(store, path=name, mode='w', shape=im.shape,
                                    chunks=CHUNKS, compressor=compressor_impl)
                x[:] = im


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
