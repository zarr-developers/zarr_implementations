IMPLEMENTATIONS=$(wildcard implementations/*)
IMPLEMENTATIONS=$(filter-out implementations/xtensor_zarr, $(IMPEMENTATIONS))

ifeq ($(TEST),) #################################################
# If TEST is not set, by default build everything, generate
# data for all implementations, and then run all pytests.

.PHONY: test data
test: data
	pytest -v -k W

data: $(IMPLEMENTATIONS)

else
# Otherwise, focus on a single implementation, only generating
# its data and using the "-k W-" keyword to limit which pytests
# get run

.PHONY: test data
test: implementations/$(TEST)
	pytest -v -k W-$(TEST)

data: implementations/$(TEST)

endif ##########################################################


data/reference_image.png:
	python generate_reference_image.py

define mk-impl-target
# For each of the items in our "implementations" directory,
# create a target which depends on the reference data and
# calls the "driver.sh" script.
#
.PHONY: $1 $1-destroy

$1: data/reference_image.png
	bash $1/driver.sh run

# Alias in case the trailing slash is included
.PHONE: $1/
$1/: $1

$1-destroy:
	bash $1/driver.sh destroy

clean: $1-destroy

endef
$(foreach impl,$(IMPLEMENTATIONS),$(eval $(call mk-impl-target,$(impl))))

.PHONY: report
report: data
	python test/test_read_all.py
