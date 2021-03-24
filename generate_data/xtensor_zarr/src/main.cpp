#include <xtensor-io/xio_gzip.hpp>
#include <xtensor-io/xio_zlib.hpp>
#include <xtensor-io/xio_blosc.hpp>
#include <xtensor-io/ximage.hpp>
#include <xtensor-zarr/xzarr_hierarchy.hpp>

using namespace xt;

int main()
{
    namespace fs = ghc::filesystem;
    const std::string hier_path = "../../../data/xtensor_zarr.zr";
    fs::remove_all(hier_path);
    fs::create_directory(hier_path);
    const auto img = load_image("../../../data/reference_image.png");

    const auto& s = img.shape();
    std::vector<size_t> shape;
    std::copy(s.cbegin(), s.cend(), std::back_inserter(shape));
    std::vector<size_t> chunk_shape = {100, 100, 1};
    auto h = create_zarr_hierarchy(hier_path, "2");
    auto g = h.create_group("/");

    // raw
    xzarr_create_array_options<xio_binary_config> raw_options;
    raw_options.fill_value = 0;
    zarray z_raw = h.create_array("/raw", shape, chunk_shape, "|u1", raw_options);
    noalias(z_raw) = img;

    // gzip
    xzarr_register_compressor<xzarr_file_system_store, xio_gzip_config>();
    xzarr_create_array_options<xio_gzip_config> gzip_options;
    gzip_options.fill_value = 0;
    zarray z_gzip = h.create_array("/gzip", shape, chunk_shape, "|u1", gzip_options);
    noalias(z_gzip) = img;

    // zlib
    xzarr_register_compressor<xzarr_file_system_store, xio_zlib_config>();
    xzarr_create_array_options<xio_zlib_config> zlib_options;
    zlib_options.fill_value = 0;
    zarray z_zlib = h.create_array("/zlib", shape, chunk_shape, "|u1", zlib_options);
    noalias(z_zlib) = img;

    // blosc
    xzarr_register_compressor<xzarr_file_system_store, xio_blosc_config>();
    xio_blosc_config blosc_config;
    blosc_config.cname = "lz4";
    xzarr_create_array_options<xio_blosc_config> blosc_options;
    blosc_options.fill_value = 0;
    blosc_options.compressor = blosc_config;
    auto g_blosc = h.create_group("/blosc/");
    zarray z_blosc_lz4 = h.create_array("/blosc/lz4", shape, chunk_shape, "|u1", blosc_options);
    noalias(z_blosc_lz4) = img;

    return 0;
}
