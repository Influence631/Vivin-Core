#defaults

SIM ?= verilator
TOPLEVEL_LANG ?= verilog
VERILOG_SOURCES += $(PWD)/../../rtl/memory.sv

#name of the top level module (dut)
COCOTB_TOPLEVEL = memory

#name of the tb file, without the .py
COCOTB_TEST_MODULES = test_memory

COMPILE_ARGS += -GMemInitFile='"init_mem.hex"'
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
