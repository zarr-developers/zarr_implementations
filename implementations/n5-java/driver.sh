ENVNAME=ZI_n5_java

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

run(){
    create_or_activate

    cd "${IMPL}"
    MVN_FLAGS=${MVN_FLAGS:-"--no-transfer-progress"}
    mvn "${MVN_FLAGS}" clean package

    java -cp target/n5_java-1.0.0.jar zarr_implementations.n5_java.App
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
