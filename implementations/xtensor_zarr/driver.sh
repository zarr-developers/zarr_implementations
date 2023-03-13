ENVNAME=ZI_xtensor_zarr

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

write(){
    create_or_activate

    cd "${IMPL}"

    set +u # Due to GDAL_DATA

    rm -rf build
    mkdir build
    cd build
    export LDFLAGS="${LDFLAGS} -Wl,-rpath,$CONDA_PREFIX/lib -Wl,-rpath,$PWD"
    export LINKFLAGS="${LDFLAGS}"
    cmake .. -DCMAKE_PREFIX_PATH=$CONDA_PREFIX -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DCMAKE_INSTALL_LIBDIR=lib
    make run
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
