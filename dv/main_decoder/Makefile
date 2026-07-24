#defaults

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

RTL := $(PWD)/../../rtl
VERILOG_SOURCES += $(RTL)/vivin_pkg.sv $(RTL)/main_decoder.sv $(RTL)/alu_decoder.sv

#name of the top level module (dut)
COCOTB_TOPLEVEL = main_decoder

#name of the tb file, without the .py
COCOTB_TEST_MODULES = test_main_decoder

#COMPILE_ARGS += -GMemInitFile='"init_mem.hex"'
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
