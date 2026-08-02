#defaults

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

RTL := $(PWD)/../../rtl
VERILOG_SOURCES += $(RTL)/vivin_pkg.sv $(RTL)/load_store_unit.sv 

#name of the top level module (dut)
COCOTB_TOPLEVEL = load_store_unit

#name of the tb file, without the .py
COCOTB_TEST_MODULES = test_load_store_unit


EXTRA_ARGS += --assert
#COMPILE_ARGS += -GMemInitFile='"init_mem.hex"'
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
