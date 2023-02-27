# cd to this directory
# https://stackoverflow.com/a/6393573/2700168
cd "${0%/*}"

Rscript install_packages.R
Rscript generate_data.R
