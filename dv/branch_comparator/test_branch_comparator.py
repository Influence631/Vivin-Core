import cocotb
from cocotb.triggers import Timer
import random
import logging
from enum import IntEnum
from dataclasses import dataclass, field

log = logging.getLogger("tb.load_store_unit")
log.setLevel(logging.INFO)
timer = Timer(1, "ns")

NTESTS = 10000

"""
typedef enum logic [2:0] {
BEQ = 3'b000,
BNE = 3'b001,
BLT = 3'b100,
BGE = 3'b101,
BLTU = 3'b110,
BGEU = 3'b111
} funct3_b_e;
"""

class BRANCH(IntEnum) :
    BEQ = 0b000
    BNE = 0b001
    BLT = 0b100
    BGE = 0b101
    BLTU = 0b110
    BGEU = 0b111

def to_signed(val, width=32):
    return val - (1 << width) if val & (1 << (width - 1)) else val 

@cocotb.test()
async def test_random(dut) :
    for i in range(NTESTS):
        rs1_u = random.randint(0, 2**32 - 1)
        rs2_u = random.randint(0, 2**32 - 1)
        branch = random.choice(list(BRANCH))

        rs1_signed = to_signed(rs1_u)
        rs2_signed = to_signed(rs2_u)

        dut.rs1_data_i.value = rs1_u
        dut.rs2_data_i.value = rs2_u
        dut.funct3_i.value = branch
        await timer

        got = dut.taken_o.value
        exp = 0
        match (branch) :
            case BRANCH.BEQ :
                exp = (rs1_u == rs2_u)
            case BRANCH.BNE :
                exp = rs1_u != rs2_u
            case BRANCH.BLT :
                exp = rs1_signed < rs2_signed 
            case BRANCH.BLTU :
                exp = rs1_u < rs2_u
            case BRANCH.BGE :
                exp = rs1_signed >= rs2_signed
            case BRANCH.BGEU :
                exp = rs1_u >= rs2_u

        assert exp == got, f"exp {exp}, got {got}" 

