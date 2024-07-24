#!/usr/bin/env bash
ENVNAME=ZI_tensorstore

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

zi_write(){
    cd "${IMPL}"
    create_or_activate
    python $IMPL/generate_tensorstore.py
}

zi_list(){
    cd "${IMPL}"
    create_or_activate
    python $IMPL/generate_tensorstore.py -list
}

zi_read(){
    cd "${IMPL}"
    create_or_activate
    python $IMPL/generate_tensorstore.py -verify "$@"
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
