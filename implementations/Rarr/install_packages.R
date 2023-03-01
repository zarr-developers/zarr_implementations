chooseCRANmirror(ind = 1)
if (!require("Rarr", quietly = TRUE)) {
    #remotes::install_git("https://git.bioconductor.org/packages/Rarr", upgrade = "never")
    remotes::install_git("https://github.com/grimbough/Rarr.git/", ref = "writing-overhangs", upgrade = "never")
}
