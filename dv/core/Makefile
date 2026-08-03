#defaults
MEM_DEPTH ?= 1024
dmemory.hex:
	python3 -c "print('00000000\n'*$(MEM_DEPTH), end='')" > $@

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

RTL := $(PWD)/../../rtl
VERILOG_SOURCES += $(RTL)/vivin_pkg.sv $(RTL)/vivin_core_top.sv 
COMPILE_ARGS += -y $(RTL) +libext+.sv

#name of the top level module (dut)
COCOTB_TOPLEVEL = vivin_core_top

#name of the tb file, without the .py
COCOTB_TEST_MODULES = test_vivin_core_top


EXTRA_ARGS += --assert
#COMPILE_ARGS += -GMemInitFile='"init_mem.hex"'
# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim
