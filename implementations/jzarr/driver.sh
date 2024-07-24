#!/usr/bin/env bash
ENVNAME=ZI_jzarr

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

zi_write(){
    create_or_activate

    cd "${IMPL}"

    MVN_FLAGS=${MVN_FLAGS:-"-q --no-transfer-progress"}
    mvn ${MVN_FLAGS} package

    java -cp target/jzarr-1.0.0.jar zarr_implementations.jzarr.App "$@" && {
        # Workaround for: https://github.com/bcdev/jzarr/issues/25
        find ../../data/jzarr* -name .zarray -exec sed -ibak 's/>u1/|u1/' {} \;
    } || {
        echo jzarr failed
        exit 2
    }
}

zi_list(){
    create_or_activate

    cd "${IMPL}"

    MVN_FLAGS=${MVN_FLAGS:-"-q --no-transfer-progress"}
    mvn ${MVN_FLAGS} package
    #notrap_outerr

    java -cp target/jzarr-1.0.0.jar zarr_implementations.jzarr.App -list
}

zi_read(){
    create_or_activate

    cd "${IMPL}"

    MVN_FLAGS=${MVN_FLAGS:-"-q --no-transfer-progress"}
    mvn ${MVN_FLAGS} package
    #notrap_outerr

    java -cp target/jzarr-1.0.0.jar zarr_implementations.jzarr.App -verify "$@"
}


. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
