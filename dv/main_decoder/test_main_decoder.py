import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
import random
import logging

log = logging.getLogger("tb.main_decoder")
log.setLevel(logging.INFO)
file_name = "instructions.hex"

#test the {opcode,func3,func7} -> control signals mapping + alu_control_o
@cocotb.test()
async def test(dut) :
    timer = Timer(1, "ns")

    with open(file_name, "r") as file :
        for line in file:
            line = line.strip()
            #print (line)

            opcode, func3, func7, exp_alu_hint = line.split(",")

            dut.opcode_i.value = opcode
            dut.func3.value = func3
            dut.func7.value = func7

            await timer(1)
            got_alu_hint = dut.alu_hint.value

            log.info(f"{opcode},  {func3}, {func7}, {exp_alu_hint}") 
