IMPLEMENTATIONS=$(wildcard implementations/*)
CURRENT_DIR = $(shell pwd)

define HELP_TEXT
make [target]

Target(s):
  write                generate data for all implementations
  list                 print directory\tpath pairs for all written data
  read                 read all data written by all implementations
  read-fast            like read, but do not re-run `write`

Notes:
  - Each implementation has a conda environment named ZI_<IMPL>

endef

export HELP_TEXT

.PHONY: help
help:
	@echo "$$HELP_TEXT"

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

.PHONY: write list read-fast read $1 $1/ $1-list $1-read-fast $1-read $1-write $1-destroy clean

write: $1-write
list: $1-list

read-fast: $1-read-fast
read: $1-read

$1-write: data/reference_image.png
	@if test -e $1/.skip; \
	    then >&2 echo "Skipping $1 -- $$(shell test -e $1/.skip && cat $1/.skip)"; \
	else \
	    bash $1/driver.sh write; \
	fi

$1-list:
	@if test -e $1/.skip; \
	    then >&2 echo "Skipping $1 -- $$(shell test -e $1/.skip && cat $1/.skip)"; \
	else \
	    bash $1/driver.sh list; \
	fi

$1-read-fast:
	@if test -e $1/.skip; \
	    then >&2 echo "Skipping $1 -- $$(shell test -e $1/.skip && cat $1/.skip)"; \
	else \
	    bash $1/driver.sh read $(DIR) $(DATASET); \
	fi


$1-read: write $1-read-fast


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
