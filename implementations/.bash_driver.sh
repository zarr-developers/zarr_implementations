#!/usr/bin/env bash
#
# This is re-usable driver code for all of the implementations.
#

set -e
set -o pipefail

argparse(){
    case "${1}" in
        write)
            [[ -z "${NODEBUG}" ]] && >&2 echo "Generating data..."
            zi_write;;
        list)
            shift;
            zi_list "$@";;
        read)
            shift;
            [[ -z "${NODEBUG}" ]] && >&2 echo "Verifying data..."
            zi_read "$@";;
        destroy)
            [[ -z "${NODEBUG}" ]] && >&2 echo "Tearing down..."
            zi_destroy;;
        *)
            [[ -z "${NODEBUG}" ]] && >&2 echo "Unknown command: ${1}"
            exit 2;;
    esac
}
