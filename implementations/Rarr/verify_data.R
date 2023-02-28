args <- commandArgs(trailingOnly = TRUE)

stopifnot(length(args) == 2)

fpath <- args[1]
ds_name <- args[2]

library(Rarr)
library(reticulate)
np <- import("numpy")

zarr_array <- file.path(fpath, ds_name)

x <- read_zarr_array(zarr_array_path = zarr_array)

a <- np$array(x)
np$savez("a.npz", a)
