# cd to this directory
# https://stackoverflow.com/a/6393573/2700168

ENVNAME=ZI_jzarr

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

run(){
    create_or_activate

    cd "${IMPL}"

    MVN_FLAGS=${MVN_FLAGS:-"--no-transfer-progress"}
    mvn "${MVN_FLAGS}" clean package

    java -cp target/jzarr-1.0.0.jar zarr_implementations.jzarr.App "$@" && {
        # Workaround for: https://github.com/bcdev/jzarr/issues/25
        find ../../data/jzarr* -name .zarray -exec sed -ibak 's/>u1/|u1/' {} \;
    } || {
        echo jzarr failed
        exit 2
    }
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
