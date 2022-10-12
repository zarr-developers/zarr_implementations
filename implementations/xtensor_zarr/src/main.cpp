#include <xtensor-io/xio_gzip.hpp>
#include <xtensor-io/xio_zlib.hpp>
#include <xtensor-io/xio_blosc.hpp>
#include <xtensor-io/ximage.hpp>
#include <xtensor-io/xnpz.hpp>
#include <xtensor-zarr/xzarr_hierarchy.hpp>

using namespace xt;

int main(int argc, char** argv)
{
    xzarr_register_compressor<xzarr_file_system_store, xio_gzip_config>();
    xzarr_register_compressor<xzarr_file_system_store, xio_zlib_config>();
    xzarr_register_compressor<xzarr_file_system_store, xio_blosc_config>();

    if (argc == 1)
    {
        namespace fs = ghc::filesystem;
        std::string hier_path_base = "../../../data/xtensor_zarr";
        const auto img = load_image("../../../data/reference_image.png");

        const auto& s = img.shape();
        std::vector<size_t> shape;
        std::copy(s.cbegin(), s.cend(), std::back_inserter(shape));
        std::vector<size_t> chunk_shape = {100, 100, 1};

        char zarr_version[2] = "2";
        const char* data_type = "|u1";

        for (int v = 2; v <= 3; v++)
        {
            if (v == 3)
            {
                zarr_version[0] = '3';
                data_type ++;
            }

            std::vector<bool> nested_values = {false, true};
            for (bool nested : nested_values)
            {
                std::string hier_path;
                char *chunk_separator;

                if (nested)
                {
                    hier_path = hier_path_base + "_nested.zr";
                    chunk_separator = (char *)"/";
                }
                else
                {
                    hier_path = hier_path_base + "_flat.zr";
                    chunk_separator = (char *)".";
                }
                if (v == 3)
                {
                    hier_path += '3';
                }

                fs::remove_all(hier_path);
                fs::create_directory(hier_path);
                auto h = create_zarr_hierarchy(hier_path.c_str(), zarr_version);
                auto g = h.create_group("/");

                // raw
                xzarr_create_array_options<xio_binary_config> raw_options;
                raw_options.fill_value = 0;
                raw_options.chunk_separator = *chunk_separator;
                zarray z_raw = h.create_array("/raw", shape, chunk_shape, data_type, raw_options);
                noalias(z_raw) = img;

                // gzip
                xzarr_create_array_options<xio_gzip_config> gzip_options;
                gzip_options.fill_value = 0;
                gzip_options.chunk_separator = *chunk_separator;
                zarray z_gzip = h.create_array("/gzip", shape, chunk_shape, data_type, gzip_options);
                noalias(z_gzip) = img;

                // zlib
                xzarr_create_array_options<xio_zlib_config> zlib_options;
                zlib_options.fill_value = 0;
                zlib_options.chunk_separator = *chunk_separator;
                zarray z_zlib = h.create_array("/zlib", shape, chunk_shape, data_type, zlib_options);
                noalias(z_zlib) = img;

                // blosc
                xio_blosc_config blosc_config;
                blosc_config.cname = "lz4";
                xzarr_create_array_options<xio_blosc_config> blosc_options;
                blosc_options.fill_value = 0;
                blosc_options.compressor = blosc_config;
                blosc_options.chunk_separator = *chunk_separator;
                auto g_blosc = h.create_group("/blosc/");
                zarray z_blosc_lz4 = h.create_array("/blosc/lz4", shape, chunk_shape, data_type, blosc_options);
                noalias(z_blosc_lz4) = img;
            }
        }
    }
    else
    {
        const std::string hier_path = argv[1];
        std::string ds_name = argv[2];
        const std::string v3_ext = ".zr3";
        std::string array_path;
        if (hier_path.compare(hier_path.length() - v3_ext.length(), v3_ext.length(), v3_ext) == 0)
        {
            array_path = hier_path;
            ds_name = "/" + ds_name;
        }
        else
        {
            array_path = hier_path + '/' + ds_name;
            ds_name = "";
        }

        auto h = get_zarr_hierarchy(array_path.c_str());
        auto z = h.get_array(ds_name);
        auto a = z.get_array<uint8_t>();

        dump_npz("a.npz", "a", a, false, false);
    }

    return 0;
}
