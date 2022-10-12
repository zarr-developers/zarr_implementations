test: data
	pytest -v

data/reference_image.png:
	python generate_reference_image.py

.PHONY: jzarr
jzarr: data/reference_image.png
	bash implementations/jzarr/generate_data.sh

.PHONY: n5java
n5java: data/reference_image.png
	bash implementations/n5-java/generate_data.sh

.PHONY: pyn5
pyn5: data/reference_image.png
	python implementations/generate_pyn5.py

.PHONY: z5py
z5py: data/reference_image.png
	python implementations/generate_z5py.py

.PHONY: zarr
zarr: data/reference_image.png
	python implementations/generate_zarr.py

.PHONY: zarrita
zarrita: data/reference_image.png
	python implementations/generate_zarrita.py

.PHONY: js
js: data/reference_image.png
	bash implementations/js/generate_data.sh

.PHONY: xtensor_zarr
xtensor_zarr: data/reference_image.png
	bash implementations/xtensor_zarr/generate_data.sh

.PHONY: data
data: jzarr n5java pyn5 z5py zarr js xtensor_zarr zarrita

.PHONY: test

.PHONY: report
report: data
	python test/test_read_all.py
