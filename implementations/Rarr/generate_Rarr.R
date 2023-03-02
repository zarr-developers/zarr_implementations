library(loder)
library(Rarr)

img <- loder::readPng("../../data/reference_image.png")

chunk_dim <- c(100, 100, 1)

for (sep in c("_flat", "_nested")) {
  for (codec in c("blosc/lz4", "zlib")) {
      
    dir_name <- paste0("Rarr", sep, ".zr")
    output_name <- file.path("../../data", dir_name, codec)

    dir.create(output_name, recursive = TRUE, showWarnings = FALSE)

    dim_sep <- ifelse(sep == "_flat", yes = ".", no = "/")

    compressor <- switch(codec,
      "blosc/lz4" = Rarr:::use_blosc(),
      "zlib" = Rarr:::use_zlib()
    )

    write_zarr_array(
      x = img,
      zarr_array_path = output_name,
      chunk_dim = chunk_dim,
      compressor = compressor,
      dimension_separator = dim_sep,
      order = "C"
    )
  }
}
