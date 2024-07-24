#!/usr/bin/env bash
ENVNAME=ZI_Rarr

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

zi_write(){
    create_or_activate

    cd "${IMPL}"

    Rscript install_packages.R
    Rscript generate_Rarr.R
}

zi_list(){
    create_or_activate

    cd "${IMPL}"

    Rscript install_packages.R
    Rscript generate_Rarr.R -list
}

zi_read(){
    create_or_activate

    cd "${IMPL}"

    Rscript install_packages.R
    Rscript verify_data.R "$@"
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
