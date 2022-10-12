# cd to this directory
# https://stackoverflow.com/a/6393573/2700168
cd "${0%/*}"

MVN_FLAGS=${MVN_FLAGS:-"--no-transfer-progress"}
mvn "${MVN_FLAGS}" clean package

java -cp target/n5_java-1.0.0.jar zarr_implementations.n5_java.App
