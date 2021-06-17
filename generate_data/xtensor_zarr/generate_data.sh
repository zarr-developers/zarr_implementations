# cd to this directory
# https://stackoverflow.com/a/6393573/2700168
cd "${0%/*}"

rm -rf build
mkdir build
cd build
export LDFLAGS="${LDFLAGS} -Wl,-rpath,$CONDA_PREFIX/lib -Wl,-rpath,$PWD"
export LINKFLAGS="${LDFLAGS}"
cmake .. -DCMAKE_PREFIX_PATH=$CONDA_PREFIX -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DCMAKE_INSTALL_LIBDIR=lib
make run
