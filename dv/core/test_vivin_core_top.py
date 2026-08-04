import cocotb
from cocotb.triggers import Timer, ClockCycles
from cocotb.clock import Clock
import random
import logging
from enum import IntEnum
from dataclasses import dataclass, field

log = logging.getLogger("tb.vivin_core_top")
log.setLevel(logging.INFO)

@cocotb.test()
async def test_random(dut) :
    Clock(dut.clk_i, 10, "ns").start()

    dut.rst_ni.value = 0

    await ClockCycles(dut.clk_i, 2)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 1000)