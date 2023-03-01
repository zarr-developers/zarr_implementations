args <- commandArgs(trailingOnly = TRUE)

stopifnot(length(args) == 2)

fpath <- args[1]
ds_name <- args[2]

library(loder)
library(Rarr)

## Read the reference image.  We strip the "loder" class so it is a 
## regular array, making the comparison easier
reference_img <- loder::readPng("data/reference_image.png")
class(reference_img) <- "array"

## read the zarr input
zarr_array <- file.path(fpath, ds_name)
x <- read_zarr_array(zarr_array_path = zarr_array)

## if the values are different quit
if(!isTRUE(all.equal(reference_img, x, check.attributes = FALSE))) {
    stop("Input and reference image are different")
}

quit(save = "no", status = 0)
