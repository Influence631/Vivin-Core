#defaults

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

RTL := $(PWD)/../../rtl
VERILOG_SOURCES += $(RTL)/vivin_pkg.sv $(RTL)/imm_gen.sv 

#name of the top level module (dut)
COCOTB_TOPLEVEL = imm_gen

#name of the tb file, without the .py
COCOTB_TEST_MODULES = test_imm_gen


EXTRA_ARGS += --assert
#COMPILE_ARGS += -GMemInitFile='"init_mem.hex"'
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
