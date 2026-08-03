# =============================================================================
#  SystemVerilog lint / tooling helpers
#
#  Single source of truth = the *.sv files in $(RTL_DIR). The editor tooling
#  file lists (lint.f for Verilator, verible.filelist for the Verible language
#  server) are GENERATED from that, so you never hand-maintain them again.
#
#    make lint       per-file Verilator lint (works on incomplete designs)
#    make elab       full-hierarchy lint from $(TOP) (once a top module exists)
#    make filelists  (re)generate lint.f + verible.filelist for the editor
#
#  All three keep the editor's lint.f / verible.filelist in sync as a side
#  effect, so running `make lint` after adding a file fixes the editor too.
# =============================================================================

RTL_DIR    ?= rtl
# top module name used by `make elab` (keep comments off this line: make
# preserves the whitespace before a trailing `#`, which would corrupt $(TOP))
TOP        ?= vivin_core_top
VERILATOR  ?= verilator
VFLAGS     ?= -Wall -Wno-EOFNEWLINE   # override to relax further, e.g. add -Wno-UNUSEDSIGNAL

SOURCES    := $(wildcard $(RTL_DIR)/*.sv)
PACKAGES   := $(shell grep -lE '^[[:space:]]*package[[:space:]]' $(RTL_DIR)/*.sv 2>/dev/null)

LINT_F     := lint.f
VERIBLE_FL := verible.filelist

.PHONY: lint elab filelists

# ---- regenerate the editor/tool file lists ----------------------------------
filelists: $(LINT_F) $(VERIBLE_FL)

# Verilator command file: -y auto-resolves modules by filename, so only the
# packages need to be listed explicitly (auto-detected from the sources).
$(LINT_F): $(SOURCES) Makefile
	@{ \
	  echo '-I$(RTL_DIR)'; \
	  echo '-y $(RTL_DIR)'; \
	  echo '+libext+.sv+.v'; \
	  for p in $(PACKAGES); do echo "$$p"; done; \
	} > $@
	@echo "regenerated $@  (packages: $(PACKAGES))"

# Verible language-server project list: every source file, flat.
$(VERIBLE_FL): $(SOURCES) Makefile
	@printf '%s\n' $(SOURCES) > $@
	@echo "regenerated $@  ($(words $(SOURCES)) files)"

# ---- per-file lint (default; tolerates incomplete designs) ------------------
lint: filelists
	@rc=0; for f in $(SOURCES); do \
	  if ! out=$$($(VERILATOR) --lint-only $(VFLAGS) -Wno-MODDUP -f $(LINT_F) "$$f" 2>&1); then \
	    echo "--- $$f"; echo "$$out"; echo; rc=1; \
	  fi; \
	done; \
	if [ $$rc -eq 0 ]; then echo "lint: clean"; else echo "lint: issues found"; fi; \
	exit $$rc

# ---- full-hierarchy lint from the top (use once $(TOP) exists) --------------
elab: filelists
	$(VERILATOR) --lint-only $(VFLAGS) -Wno-MODDUP -f $(LINT_F) \
	  --top-module $(TOP) $(RTL_DIR)/$(TOP).sv
