#!/usr/bin/env bash
#
# This is re-usable driver code for all of the implementations
# that make use of a conda environment file.
#

set -e
set -o pipefail

## Setup based on mamba versus conda installation
if command -v mamba &> /dev/null
then
    COMMAND=mamba
else
    COMMAND=conda
fi

create_or_activate(){

    if { $COMMAND env list | grep $ENVNAME; } >/dev/null 2>&1; then
        [[ -z "${NODEBUG}" ]] && >&2 echo "Using $ENVNAME"
    else
        [[ -z "${NODEBUG}" ]] && >&2 echo "Creating $ENVNAME"
        $COMMAND env create -n $ENVNAME -f $IMPL/environment.yml
    fi
    export MAMBA_ROOT_PREFIX=$(conda info --base -q)
    export MAMBA_EXE=${MAMBA_ROOT_PREFIX}/bin/mamba
    export CONDA_EXE=${MAMBA_ROOT_PREFIX}/bin/conda
    . $MAMBA_ROOT_PREFIX/etc/profile.d/conda.sh
    . $MAMBA_ROOT_PREFIX/etc/profile.d/mamba.sh

    [[ -z "${NODEBUG}" ]] && >&2 echo "Activating $ENVNAME"
    $COMMAND activate $ENVNAME
}

zi_destroy(){

    if { $COMMAND env list | grep $ENVNAME; } >/dev/null 2>&1; then
        [[ -z "${NODEBUG}" ]] && >&2 echo "Destroying $ENVNAME"
        $COMMAND env remove -y -n $ENVNAME
    else
        >&2 echo "No known env: $ENVNAME"
    fi
}
