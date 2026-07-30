import cocotb
from cocotb.triggers import Timer
import random
import logging
from enum import IntEnum
from dataclasses import dataclass

log = logging.getLogger("tb.imm_gen")
log.setLevel(logging.INFO)
timer = Timer(1, "ns")

N_RANDOM = 2000
MASK32 = 0xFFFF_FFFF


class ImmSel(IntEnum) :
    IMM_I = 0
    IMM_S = 1
    IMM_B = 2
    IMM_U = 3
    IMM_J = 4


def bits(val, hi, lo) :
    """extract val[hi:lo] as an unsigned int"""
    return (val >> lo) & ((1 << (hi - lo + 1)) - 1)


# each format stores ONE semantic immediate (a plain signed python int) plus the
# don't-care fields, randomized to prove imm_gen ignores them. encode() scatters
# the immediate into instruction bit positions per the RISC-V unprivileged spec
# (sec 2.3, Immediate Encoding Variants) -- the inverse of what imm_gen does.
# expected data_o is just the immediate itself as a 32-bit two's complement pattern.
#
# the opcode never reaches imm_gen (port is instr_i[31:7]) -- it is carried and
# randomized over the format's legal opcodes so encode() emits real instructions,
# reusable later for core-level tests.

@dataclass
class IInstr :
    imm : int           # 12-bit signed
    rs1 : int = 0
    funct3 : int = 0
    rd : int = 0
    opcode : int = 0b0010011

    imm_sel = ImmSel.IMM_I
    opcodes = [0b0010011, 0b0000011, 0b1100111]     # OP-IMM, LOAD, JALR

    def __post_init__(self) :
        assert -2048 <= self.imm <= 2047, f"I imm out of range: {self.imm}"

    @classmethod
    def random(cls) :
        return cls(imm=random.randint(-2048, 2047),
                   rs1=random.getrandbits(5),
                   funct3=random.getrandbits(3),
                   rd=random.getrandbits(5),
                   opcode=random.choice(cls.opcodes))

    def encode(self) :
        pat = self.imm & 0xFFF
        return ((bits(pat, 11, 0) << 20)    # inst[31:20] = imm[11:0]
                | (self.rs1 << 15)
                | (self.funct3 << 12)
                | (self.rd << 7)
                | self.opcode)

    def expected(self) :
        return self.imm & MASK32


@dataclass
class SInstr :
    imm : int           # 12-bit signed
    rs1 : int = 0
    rs2 : int = 0
    funct3 : int = 0
    opcode : int = 0b0100011

    imm_sel = ImmSel.IMM_S
    opcodes = [0b0100011]                           # STORE

    def __post_init__(self) :
        assert -2048 <= self.imm <= 2047, f"S imm out of range: {self.imm}"

    @classmethod
    def random(cls) :
        return cls(imm=random.randint(-2048, 2047),
                   rs1=random.getrandbits(5),
                   rs2=random.getrandbits(5),
                   funct3=random.getrandbits(3),
                   opcode=random.choice(cls.opcodes))

    def encode(self) :
        pat = self.imm & 0xFFF
        return ((bits(pat, 11, 5) << 25)    # inst[31:25] = imm[11:5]
                | (self.rs2 << 20)
                | (self.rs1 << 15)
                | (self.funct3 << 12)
                | (bits(pat, 4, 0) << 7)    # inst[11:7] = imm[4:0]
                | self.opcode)

    def expected(self) :
        return self.imm & MASK32


@dataclass
class BInstr :
    imm : int           # 13-bit signed, even
    rs1 : int = 0
    rs2 : int = 0
    funct3 : int = 0
    opcode : int = 0b1100011

    imm_sel = ImmSel.IMM_B
    opcodes = [0b1100011]                           # BRANCH

    def __post_init__(self) :
        assert -4096 <= self.imm <= 4094, f"B imm out of range: {self.imm}"
        assert self.imm % 2 == 0, f"B imm must be even: {self.imm}"

    @classmethod
    def random(cls) :
        return cls(imm=random.randrange(-4096, 4096, 2),
                   rs1=random.getrandbits(5),
                   rs2=random.getrandbits(5),
                   funct3=random.getrandbits(3),
                   opcode=random.choice(cls.opcodes))

    def encode(self) :
        pat = self.imm & 0x1FFF
        return ((bits(pat, 12, 12) << 31)   # inst[31]    = imm[12]
                | (bits(pat, 10, 5) << 25)  # inst[30:25] = imm[10:5]
                | (self.rs2 << 20)
                | (self.rs1 << 15)
                | (self.funct3 << 12)
                | (bits(pat, 4, 1) << 8)    # inst[11:8]  = imm[4:1]
                | (bits(pat, 11, 11) << 7)  # inst[7]     = imm[11]
                | self.opcode)

    def expected(self) :
        return self.imm & MASK32


@dataclass
class UInstr :
    imm : int           # full 32-bit value, low 12 bits zero
    rd : int = 0
    opcode : int = 0b0110111

    imm_sel = ImmSel.IMM_U
    opcodes = [0b0110111, 0b0010111]                # LUI, AUIPC

    def __post_init__(self) :
        assert 0 <= self.imm <= MASK32, f"U imm out of range: {self.imm:#x}"
        assert self.imm & 0xFFF == 0, f"U imm[11:0] must be zero: {self.imm:#x}"

    @classmethod
    def random(cls) :
        return cls(imm=random.getrandbits(20) << 12,
                   rd=random.getrandbits(5),
                   opcode=random.choice(cls.opcodes))

    def encode(self) :
        return (self.imm                    # inst[31:12] = imm[31:12]
                | (self.rd << 7)
                | self.opcode)

    def expected(self) :
        return self.imm


@dataclass
class JInstr :
    imm : int           # 21-bit signed, even
    rd : int = 0
    opcode : int = 0b1101111

    imm_sel = ImmSel.IMM_J
    opcodes = [0b1101111]                           # JAL

    def __post_init__(self) :
        assert -(1 << 20) <= self.imm <= (1 << 20) - 2, f"J imm out of range: {self.imm}"
        assert self.imm % 2 == 0, f"J imm must be even: {self.imm}"

    @classmethod
    def random(cls) :
        return cls(imm=random.randrange(-(1 << 20), 1 << 20, 2),
                   rd=random.getrandbits(5),
                   opcode=random.choice(cls.opcodes))

    def encode(self) :
        pat = self.imm & 0x1F_FFFF
        return ((bits(pat, 20, 20) << 31)   # inst[31]    = imm[20]
                | (bits(pat, 10, 1) << 21)  # inst[30:21] = imm[10:1]
                | (bits(pat, 11, 11) << 20) # inst[20]    = imm[11]
                | (bits(pat, 19, 12) << 12) # inst[19:12] = imm[19:12]
                | (self.rd << 7)
                | self.opcode)

    def expected(self) :
        return self.imm & MASK32


FORMATS = [IInstr, SInstr, BInstr, UInstr, JInstr]


async def drive_and_check(dut, instr) :
    dut.imm_sel_i.value = instr.imm_sel
    dut.instr_i.value = instr.encode() >> 7     # port is instr_i[31:7]

    await timer

    got = dut.data_o.value.to_unsigned()
    exp = instr.expected()
    assert got == exp, (f"{type(instr).__name__} imm={instr.imm} "
                       f"instr={instr.encode():032b} exp={exp:#010x} got={got:#010x}")


@cocotb.test()
async def test_random(dut) :
    for cls in FORMATS :
        for _ in range(N_RANDOM) :
            await drive_and_check(dut, cls.random())


# corners: zero, +-smallest, all-ones (-1 / -2), max positive, most negative --
# sign-extension bugs live at the sign-bit boundary
corner_imms = {
    IInstr : [0, 1, -1, 2047, -2048],
    SInstr : [0, 1, -1, 2047, -2048],
    BInstr : [0, 2, -2, 4094, -4096],
    UInstr : [0, 1 << 12, 0x8000_0000, 0xFFFF_F000],
    JInstr : [0, 2, -2, (1 << 20) - 2, -(1 << 20)],
}

@cocotb.test()
async def test_corners(dut) :
    for cls in FORMATS :
        for imm in corner_imms[cls] :
            await drive_and_check(dut, cls(imm=imm))
