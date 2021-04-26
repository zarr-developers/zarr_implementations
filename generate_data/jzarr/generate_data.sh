# cd to this directory
# https://stackoverflow.com/a/6393573/2700168
cd "${0%/*}"

mvn clean package
java -cp target/jzarr-1.0.0.jar zarr_implementations.jzarr.App "$@"
