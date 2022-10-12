IMPLEMENTATIONS=$(wildcard implementations/*)

ifeq ($(TEST),)
# If TEST is not set, by default build everything, generate
# data for all implementations, and then run all pytests.

.PHONY: test
test: data
	pytest -v -k W

else
# Otherwise, focus on a single implementation, only generating
# its data and using the "-k W-" keyword to limit which pytests
# get run

.PHONY: test
test: implementations/$(TEST)
	pytest -v -k W-$(TEST)

endif

data/reference_image.png:
	python generate_reference_image.py

.PHONY: $(IMPLEMENTATIONS)
implementations/%: data/reference_image.png
	bash $^/driver.sh

.PHONY: report
report: data
	python test/test_read_all.py
