#!/usr/bin/env bash
ENVNAME=ZI_js

# Standard bootstrapping
IMPL=$( cd -- "$( dirname -- "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )
ROOT=$( dirname $IMPL)

zi_write(){
    create_or_activate

    cd "${IMPL}"

    npm install
    npm start
}

zi_list(){
    create_or_activate

    cd "${IMPL}"

    npm install --silent
    npm run --silent start -- --list "$@"
}

zi_read(){
    cd "${IMPL}"
    npm run start -- --verify "$@"
}

. $ROOT/.conda_driver.sh
. $ROOT/.bash_driver.sh
argparse "$@"
