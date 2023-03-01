library(loder)
library(Rarr)

img <- loder::readPng("../../data/reference_image.png")

chunk_dim <- c(100, 100, 1)

for(codec in c("blosc/lz4", "zlib")) {

  output_name <- file.path("../../data", "Rarr.zr", codec)
  
  dir.create(output_name, recursive = TRUE, showWarnings = FALSE)
  
  compressor <- switch (codec,
    "blosc/lz4" = Rarr:::use_blosc(),
    "zlib"  = Rarr:::use_zlib() 
  )
  
  write_zarr_array(x = img, 
                   zarr_array_path = output_name,
                   chunk_dim = chunk_dim, 
                   compressor = compressor, 
                   order = "C")
}
