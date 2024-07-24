#!/usr/bin/env bash
ENVNAME=ZI_n5_java

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

zi_write(){
    create_or_activate

    cd "${IMPL}"
    MVN_FLAGS=${MVN_FLAGS:-"-q --no-transfer-progress"}
    mvn ${MVN_FLAGS} package

    java -cp target/n5_java-1.0.0.jar zarr_implementations.n5_java.App
}

zi_list(){
    create_or_activate

    cd "${IMPL}"
    MVN_FLAGS=${MVN_FLAGS:-"-q --no-transfer-progress"}
    mvn ${MVN_FLAGS} package

    java -cp target/n5_java-1.0.0.jar zarr_implementations.n5_java.App -list
}

zi_read(){
    create_or_activate

    cd "${IMPL}"
    MVN_FLAGS=${MVN_FLAGS:-"-q --no-transfer-progress"}
    mvn ${MVN_FLAGS} package

    java -cp target/n5_java-1.0.0.jar zarr_implementations.n5_java.App -verify "$@"
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
