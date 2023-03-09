ENVNAME=ZI_Rarr

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

run(){
    create_or_activate

    cd "${IMPL}"

    Rscript install_packages.R
    Rscript generate_Rarr.R
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
