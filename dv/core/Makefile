#defaults
MEM_DEPTH ?= 1024
PROG ?= 01_addi
VERILATOR_TRACE ?= 1

SIM ?= verilator
TOPLEVEL_LANG ?= verilog

RTL := $(CURDIR)/../../rtl
VERILOG_SOURCES += $(RTL)/vivin_pkg.sv $(RTL)/vivin_core_top.sv 
COMPILE_ARGS += -y $(RTL) +libext+.sv

COCOTB_TOPLEVEL = vivin_core_top
COCOTB_TEST_MODULES = test_vivin_core_top

EXTRA_ARGS += --assert
CUSTOM_COMPILE_DEPS += $(wildcard $(RTL)/*.sv)
CUSTOM_SIM_DEPS += imemory.hex dmemory.hex

# include cocotb's make rules to take care of the simulator setup
include $(shell cocotb-config --makefiles)/Makefile.sim

.DEFAULT_GOAL := fresh
.PHONY: fresh
fresh:
	$(MAKE) clean
	$(MAKE) sim

programs/%.hex: programs/%.s
	riscv64-unknown-elf-as -march=rv32i -mabi=ilp32 -o $*.o $<
	riscv64-unknown-elf-ld -m elf32lriscv -Ttext=0 -o $*.elf $*.o
	riscv64-unknown-elf-objcopy -O binary $*.elf $*.bin
	od -An -tx4 -w4 -v $*.bin | tr -d ' ' > $@
	$(RM) $*.o $*.elf $*.bin

.PHONY: imemory.hex surfer
imemory.hex: programs/$(PROG).hex
	cp -f $< $@

dmemory.hex:
	python3 -c "print('00000000\n'*$(MEM_DEPTH), end='')" > $@

clean::
	$(RM) -f imemory.hex dmemory.hex

surfer: dump.vcd
	surfer -s ./dump.surf.ron ./dump.vcd