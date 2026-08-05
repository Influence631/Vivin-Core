import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
import random
import logging
from enum import IntEnum
from dataclasses import dataclass, replace

log = logging.getLogger("tb.main_decoder")
log.setLevel(logging.INFO)
file_name = "instructions.hex"
timer = Timer(1, "ns")

OPCODE_OP_IMM = 0b0010011
OPCODE_OP     = 0b0110011

mnem_opcode_map = {
    #OPCODE_LUI
    "LUI"   : 0b0110111,
    #opcode_auipc
    "AUIPC" : 0b0010111,
    #opcode_jal
    "JAL"   : 0b1101111,
    #opcode_jalr
    "JALR"  : 0b1100111,
    #opcode_branch
    "BEQ"   : 0b1100011,
    "BNE"   : 0b1100011,
    "BLT"   : 0b1100011,
    "BGE"   : 0b1100011,
    "BLTU"  : 0b1100011,
    "BGEU"  : 0b1100011,
    #opcode_load
    "LB"    : 0b0000011,
    "LH"    : 0b0000011,
    "LW"    : 0b0000011,
    "LBU"   : 0b0000011,
    "LHU"   : 0b0000011,
    #opcode_store
    "SB"    : 0b0100011,
    "SH"    : 0b0100011,
    "SW"    : 0b0100011,
    #opcode_imm_op
    "ADDI"  : 0b0010011,
    "SLTI"  : 0b0010011,
    "SLTIU" : 0b0010011,
    "XORI"  : 0b0010011,
    "ORI"   : 0b0010011,
    "ANDI"  : 0b0010011,
    "SLLI"  : 0b0010011,
    "SRLI"  : 0b0010011,
    "SRAI"  : 0b0010011,
    #opcode_op
    "ADD"   : 0b0110011,
    "SUB"   : 0b0110011,
    "SLL"   : 0b0110011,
    "SLT"   : 0b0110011,
    "SLTU"  : 0b0110011,
    "XOR"   : 0b0110011,
    "SRL"   : 0b0110011,
    "SRA"   : 0b0110011,
    "OR"    : 0b0110011,
    "AND"   : 0b0110011,
    #opcode_misc_mem
    "FENCE" : 0b0001111,
    #opcode_system
    "ECALL" : 0b1110011,
    "EBREAK": 0b1110011,
}

class ALU_OP(IntEnum) :
    ALU_ADD = 0
    ALU_SUB = 1
    ALU_SLT = 2
    ALU_SLTU = 3
    ALU_AND = 4
    ALU_OR = 5
    ALU_XOR = 6
    ALU_SLL = 7
    ALU_SRL = 8
    ALU_SRA = 9


class ImmSel(IntEnum) :
    IMM_I = 0
    IMM_S = 1
    IMM_B = 2
    IMM_U = 3
    IMM_J = 4

class ResSel(IntEnum) :
    ALU_RES = 0
    MEM_RES = 1
    PC4_RES = 2

class OP_A_SEL(IntEnum) :
    OP_A_RS1 = 0
    OP_A_PC = 1 
    OP_A_ZERO = 2

class OP_B_SEL(IntEnum) :
    OP_B_RS2 = 0
    OP_B_IMM = 1


@dataclass(slots=True)
class ControlSignals :
    is_store : int = 0
    is_load : int = 0
    reg_write : int = 0

    op_a_sel : OP_A_SEL = OP_A_SEL.OP_A_RS1  #rs1  
    op_b_sel : OP_B_SEL = OP_B_SEL.OP_B_RS2 #rs2

    alu_op : ALU_OP = ALU_OP.ALU_ADD #add

    sys_halt : int = 0
    illegal_instr : int = 0
    branch : int = 0
    jump : int = 0

    imm_sel : int = 0 #imm_i
    result_sel : ResSel = ResSel.ALU_RES

opcode_to_control_sig = {
    #opcode_lui
    0b0110111 : ControlSignals(reg_write=1, op_a_sel=OP_A_SEL.OP_A_ZERO, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_U),
    #opcode_auipc
    0b0010111 : ControlSignals(reg_write=1, op_a_sel=OP_A_SEL.OP_A_PC, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_U),
    #opcode_jal
    0b1101111 : ControlSignals(reg_write=1, jump=1, op_a_sel=OP_A_SEL.OP_A_PC, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_J, result_sel=ResSel.PC4_RES),
    #opcode_jalr
    0b1100111 : ControlSignals(reg_write=1, jump=1, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_I, result_sel=ResSel.PC4_RES),
    #opcode_branch
    0b1100011 : ControlSignals(branch=1, op_a_sel=OP_A_SEL.OP_A_PC, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_B),
    #opcode_load
    0b0000011 : ControlSignals(reg_write=1, is_load = 1, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_I, result_sel=ResSel.MEM_RES),
    #opcode_store
    0b0100011 : ControlSignals(is_store=1, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_S),
    #opcode_imm_op
    0b0010011 : ControlSignals(reg_write=1, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_I),
    #opcode_op
    0b0110011 : ControlSignals(reg_write=1),
    #opcode_misc_mem (fence = NOP in single-cycle)
    0b0001111 : ControlSignals(),
    #opcode_system (ecall/ebreak -> halt)
    0b1110011 : ControlSignals(sys_halt=1),
}

#test the {opcode,func3,func7} -> control signals mapping + alu_control_o
@cocotb.test()
async def test(dut) :
     with open(file_name, "r") as file :
        for line in file:
            line = line.strip()
            #print (line)

            mnemonic, funct3, funct7, exp_alu_op = line.split(",")
            opcode = int(mnem_opcode_map[mnemonic])
            exp_control = replace(opcode_to_control_sig[opcode], alu_op=ALU_OP[exp_alu_op])
                        

            funct3 =  0 if funct3 == "x" else int(funct3, 2)
            funct7 =  0 if funct7 == "x" else int(funct7, 2)

            dut.opcode_i.value = opcode
            dut.funct3_i.value = funct3
            dut.funct7_i.value = funct7

            await timer

            alu_op = ALU_OP(dut.alu_op_o.value)
            reg_write = int(dut.reg_write_o.value)
            is_store = int(dut.is_store_o.value)
            is_load = int(dut.is_load_o.value)
            imm_sel = ImmSel(dut.imm_sel_o.value)
            op_b_sel = OP_B_SEL(dut.op_b_sel_o.value)
            op_a_sel = OP_A_SEL(dut.op_a_sel_o.value)
            res_sel = ResSel(dut.result_sel_o.value)
            branch = int(dut.branch_o.value)
            jump = int(dut.jump_o.value)
            sys_halt = int(dut.sys_halt_o.value)
            illegal_instr = int(dut.illegal_instr_o.value)

            control = ControlSignals(
                reg_write=reg_write,
                is_store=is_store,
                is_load=is_load,
                op_a_sel=op_a_sel,
                op_b_sel=op_b_sel,
                alu_op=alu_op,
                sys_halt=sys_halt,
                illegal_instr=illegal_instr,
                branch=branch,
                jump=jump,
                result_sel=res_sel,
                imm_sel=imm_sel
            )

            assert control == exp_control, f"\nEXPECTED CONTROL for command {mnemonic}\n\n {exp_control}, \n\n RECEIVED CONTROL : \n\n {control}"
        

#every opcode outside the 11 legal ones must decode to halt
@cocotb.test()
async def test_illegal_opcodes(dut) :
    legal_opcodes = set(mnem_opcode_map.values())

    for opcode in range(128) :
        if opcode in legal_opcodes :
            continue

        dut.opcode_i.value = opcode
        dut.funct3_i.value = random.getrandbits(3)
        dut.funct7_i.value = random.getrandbits(7)

        await timer

        assert int(dut.illegal_instr_o.value) == 1, f"illegal_instr not asserted for illegal opcode {opcode:07b}"

        #an illegal opcode must not request any architectural side effect
        for sig in ("reg_write_o", "is_store_o", "is_load_o", "branch_o", "jump_o") :
            assert int(getattr(dut, sig).value) == 0, f"{sig} asserted for illegal opcode {opcode:07b}"

#opcodes that carry no funct7: only these funct3 encodings are legal
LEGAL_FUNCT3 = {
    0b0000011 : {0b000, 0b001, 0b010, 0b100, 0b101}, # LOAD LB LH LW LBU LHU
    0b0100011 : {0b000, 0b001, 0b010}, # STORE SB SH SW
    0b1100011 : {0b000, 0b001, 0b100, 0b101, 0b110, 0b111}, # BRANCH (010/011 illegal)
    0b1100111 : {0b000}, # JALR
    0b0001111 : {0b000}, # FENCE
    0b1110011 : {0b000}, # SYSTEM
    0b0110111 : set(range(8)), # LUI   U-type, no funct3 field
    0b0010111 : set(range(8)), # AUIPC U-type, no funct3 field
    0b1101111 : set(range(8)), # JAL   J-type, no funct3 field
}

def expect_illegal(opcode, funct3, funct7):
    #Reference model: is this opcode/funct3/funct7 combination illegal
    if opcode == OPCODE_OP_IMM:
        # bits 31:25 are IMMEDIATE bits, not funct7, only shifts constrain them
        if funct3 == 0b001: # SLLI
            return funct7 != 0b0000000
        if funct3 == 0b101: # SRLI / SRAI
            return funct7 not in (0b0000000, 0b0100000)
        return False #for the rest of immediate ops, every "funct7" is valid because its imm value
    if opcode == OPCODE_OP:
        if funct3 in (0b000, 0b101): # ADD/SUB, SRL/SRA
            return funct7 not in (0b0000000, 0b0100000)
        return funct7 != 0b0000000 #the rest of reg operations must have funct7 set to '0 
    if opcode in LEGAL_FUNCT3:
        return funct3 not in LEGAL_FUNCT3[opcode]
    return True #not one of the 11 legal opcodes

def expect_alu_op(opcode, funct3, funct7):
    #Reference model: which alu_op should this funct3/funct7 decode to
    is_reg = (opcode == OPCODE_OP)
    f7_5 = (funct7 >> 5) & 1
    return {
        #only OP may turn funct7[5] into a SUB, for OP_IMM it is an immediate bit
        0b000 : ALU_OP.ALU_SUB if (is_reg and f7_5) else ALU_OP.ALU_ADD,
        0b001 : ALU_OP.ALU_SLL,
        0b010 : ALU_OP.ALU_SLT,
        0b011 : ALU_OP.ALU_SLTU,
        0b100 : ALU_OP.ALU_XOR,
        0b101 : ALU_OP.ALU_SRA if f7_5 else ALU_OP.ALU_SRL,
        0b110 : ALU_OP.ALU_OR,
        0b111 : ALU_OP.ALU_AND,
    }[funct3]

@cocotb.test()
async def test_decode_sweep(dut):
    #exhaustive over opcode x funct3, and over funct7 for the two opcodes where it carries meaning
    for opcode in range(128):
        f7_vals = range(128) if opcode in (OPCODE_OP_IMM, OPCODE_OP) \
                             else (0b0000000, 0b0100000, 0b1111111)
        for funct3 in range(8):
            for funct7 in f7_vals:
                dut.opcode_i.value = opcode
                dut.funct3_i.value = funct3
                dut.funct7_i.value = funct7
                await timer

                exp = expect_illegal(opcode, funct3, funct7)
                got = bool(int(dut.illegal_instr_o.value))
                assert got == exp, (
                    f"opcode={opcode:07b} funct3={funct3:03b} funct7={funct7:07b}: "
                    f"expected illegal={exp}, got {got}"
                )

                #alu_op is only elaborated for OP / OP_IMM, and only meaningful when legal
                if not exp and opcode in (OPCODE_OP_IMM, OPCODE_OP) :
                    exp_op = expect_alu_op(opcode, funct3, funct7)
                    got_op = ALU_OP(dut.alu_op_o.value)
                    assert got_op == exp_op, (
                        f"opcode={opcode:07b} funct3={funct3:03b} funct7={funct7:07b}: "
                        f"expected {exp_op.name}, got {got_op.name}"
                    )