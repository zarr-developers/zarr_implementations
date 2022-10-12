#!/usr/bin/env bash
#

ENVNAME=ZI_zarritz

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)
. $ROOT/.conda_driver.sh
create_or_activate

python $IMPL/generate_zarrita.py
