#!/usr/bin/env bash
#
#

ENVNAME=ZI_zarr_python

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

run(){
    create_or_activate
    python $IMPL/generate_zarr.py
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
