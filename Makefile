IMPLEMENTATIONS=$(wildcard implementations/*)


ifeq ($(TEST),)
# If TEST is not set, by default build everything, generate
# data for all implementations, and then run all pytests.

.PHONY: test
test: data
	pytest -v -k W

else
# Otherwise, focus on a single implementation.

.PHONY: test
test: $(TEST)
	pytest -v -k $(TEST)

endif

data/reference_image.png:
	python generate_reference_image.py

.PHONY: report
report: data
	python test/test_read_all.py

#
# Implementations
#

.PHONY: implementations/jzarr
implementations/jzarr: data/reference_image.png
	bash implementations/jzarr/driver.sh

.PHONY: implementations/n5java
implementations/n5java: data/reference_image.png
	bash implementations/n5-java/generate_data.sh

.PHONY: implementations/pyn5
implementations/pyn5: data/reference_image.png
	python implementations/generate_pyn5.py

.PHONY: implementations/z5py
implementations/z5py: data/reference_image.png
	python implementations/generate_z5py.py

.PHONY: implementations/zarr-python
implementations/zarr-python: data/reference_image.png
	python implementations/generate_zarr.py

.PHONY: implementations/zarrita
implementations/zarrita: data/reference_image.png
	python implementations/generate_zarrita.py

.PHONY: implementations/js
implementations/js: data/reference_image.png
	bash implementations/js/generate_data.sh

.PHONY: implementations/xtensor_zarr
implementations/xtensor_zarr: data/reference_image.png
	bash implementations/xtensor_zarr/generate_data.sh
