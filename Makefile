IMPLEMENTATIONS=$(wildcard implementations/*)

#
# The default target:
# (1) creates an environment for all implementations (if needed),
# (2) generates sample data for all implementations, and
# (3) runs tests against that sample data for all implementations.
#

.PHONY: report

report: data
	python test/test_read_all.py

.PHONY: test data

ifeq ($(TEST),) #################################################
# If TEST is not set, by default build everything, generate
# data for all implementations, and then run all pytests.

test: data
	pytest -v -k W

data: $(IMPLEMENTATIONS)

else
# Otherwise, focus on a single implementation, only generating
# its data and using the "-k W-" keyword to limit which pytests
# get run

test: implementations/$(TEST)
	pytest -v -k W-$(TEST)

data: implementations/$(TEST)

endif ##########################################################


data/reference_image.png:
	python generate_reference_image.py


define mk-impl-target
# For each of the items in our "implementations" directory,
# create targets which depend on the reference data and
# call the "driver.sh" script as necessary.

.PHONY: read write $1 $1/ $1-read $1-write $1-destroy clean

read: $1-read
write: $1-write

$1-write: data/reference_image.png
	bash $1/driver.sh write

# Alias for read & write
$1: $1-write $1-read

# Alias in case the trailing slash is included
$1/: $1

# Additional target to cleanup the environment
$1-destroy:
	bash $1/driver.sh destroy

clean: $1-destroy

endef
$(foreach impl,$(IMPLEMENTATIONS),$(eval $(call mk-impl-target,$(impl))))
