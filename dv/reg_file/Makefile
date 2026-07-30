#defaults

SIM ?= verilator
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../../rtl/reg_file.sv

#name of the top level module (dut)
COCOTB_TOPLEVEL = reg_file

#name of the tb file, without the .py
COCOTB_TEST_MODULES = test_reg_file

EXTRA_ARGS += --assert
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim