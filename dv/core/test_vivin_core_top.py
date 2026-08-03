import cocotb
from cocotb.triggers import Timer
import random
import logging
from enum import IntEnum
from dataclasses import dataclass, field

log = logging.getLogger("tb.vivin_core_top")
log.setLevel(logging.INFO)
timer = Timer(1, "ns")

@cocotb.test()
async def test_random(dut) :
    pass