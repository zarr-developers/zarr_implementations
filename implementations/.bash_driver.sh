#!/usr/bin/env bash
#
# This is re-usable driver code for all of the implementations.
#

set -e
set -o pipefail

argparse(){
    case "${1}" in
        run)
            echo "Running driver..."
            run;;
        destroy)
            echo "Tearing down..."
            destroy;;
        *)
            echo "Unknown command: ${1}"
            exit 2;;
    esac
}
