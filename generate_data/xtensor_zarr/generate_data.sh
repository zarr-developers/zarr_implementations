# cd to this directory
# https://stackoverflow.com/a/6393573/2700168
cd "${0%/*}"

rm -rf build
mkdir build
cd build
cmake .. -DCMAKE_PREFIX_PATH=$CONDA_PREFIX -DCMAKE_INSTALL_PREFIX=$CONDA_PREFIX -DCMAKE_INSTALL_LIBDIR=lib
make run
