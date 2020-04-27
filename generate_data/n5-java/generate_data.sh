# cd to this directory
# https://stackoverflow.com/a/6393573/2700168
cd "${0%/*}"

# clean the n5 data. ideally, this would be done in n5-java, but I don't know if
# it supports truncate mode
rm -r ../../data/n5-java.n5

mvn clean package
java -cp target/n5_java-1.0.0.jar zarr_implementations.n5_java.App
