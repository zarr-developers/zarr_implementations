#!/usr/bin/env bash
#
#

ENVNAME=ZI_pyn5

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

run(){
    create_or_activate
    python $IMPL/generate_pyn5.py
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
