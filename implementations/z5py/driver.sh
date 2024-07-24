#!/usr/bin/env bash
ENVNAME=ZI_z5py

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

zi_write(){
    cd "${IMPL}"
    create_or_activate
    python $IMPL/generate_z5py.py
}

zi_list(){
    cd "${IMPL}"
    create_or_activate
    python $IMPL/generate_z5py.py -list
}

zi_read(){
    cd "${IMPL}"
    create_or_activate
    python $IMPL/generate_z5py.py -verify "$@"
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
