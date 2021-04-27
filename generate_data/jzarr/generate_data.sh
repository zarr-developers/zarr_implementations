# cd to this directory
# https://stackoverflow.com/a/6393573/2700168
cd "${0%/*}"

set -e
set -u
set -x

mvn clean package
java -cp target/jzarr-1.0.0.jar zarr_implementations.jzarr.App "$@" && {
    # Workaround for: https://github.com/bcdev/jzarr/issues/25
    find ../../data/jzarr* -name .zarray -exec sed -ibak 's/>u1/|u1/' {} \;
} || {
    echo jzarr failed
    exit 2
}

