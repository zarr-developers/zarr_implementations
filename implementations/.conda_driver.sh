#!/usr/bin/env bash
#
# This is re-usable driver code for all of the implementations
# that make use of a conda environment file.
#

set -e
set -o pipefail

create_or_activate(){
    if { conda env list | grep $ENVNAME; } >/dev/null 2>&1; then
        echo "Using $ENVNAME"
    else
        echo "Creating $ENVNAME"
        conda env create -n $ENVNAME -f $IMPL/environment.yml
    fi
    eval "$(conda shell.bash hook)"
    echo "Activating $ENVNAME"
    conda activate $ENVNAME
}

destroy(){
    if { conda env list | grep $ENVNAME; } >/dev/null 2>&1; then
        echo "Destroying $ENVNAME"
        conda env remove -y -n $ENVNAME
    else
        echo "No known env: $ENVNAME"
    fi
}
