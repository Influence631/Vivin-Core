import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
import random
import logging
from enum import IntEnum
from dataclasses import dataclass

log = logging.getLogger("tb.main_decoder")
log.setLevel(logging.INFO)
file_name = "instructions.hex"
timer = Timer(1, "ns")

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

"""
typedef enum logic [2:0] {
    IMM_I,
    IMM_S,
    IMM_B,
    IMM_U,
    IMM_J
  } imm_sel_e;
"""

class ResSel(IntEnum) :
    ALU_RES = 0
    MEM_RES = 1
    PC4_RES = 2

"""
typedef enum logic [1:0] {
    ALU_RES,
    MEM_RES,
    PC4_RES
} result_sel_e;
"""

class OP_A_SEL(IntEnum) :
    OP_A_RS1 = 0
    OP_A_PC = 1 
    OP_A_ZERO = 2

"""
typedef enum logic [1:0] {
    OP_A_RS1, //normal
    OP_A_PC, //auipc, jal
    OP_A_ZERO //lui
} op_a_sel_e;
"""

class OP_B_SEL(IntEnum) :
    OP_B_RS2 = 0
    OP_B_IMM = 1

"""
typedef enum logic {
    OP_B_RS2,
    OP_B_IMM
} op_b_sel_e;

"""

@dataclass(slots=True)
class ControlSignals :
    mem_write : int = 0
    reg_write : int = 0

    op_a_sel : OP_A_SEL = OP_A_SEL.OP_A_RS1  #rs1  
    op_b_sel : OP_B_SEL = OP_B_SEL.OP_B_RS2 #rs2

    alu_op : ALU_OP = ALU_OP.ALU_ADD #add

    halt : int = 0
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
    0b0000011 : ControlSignals(reg_write=1, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_I, result_sel=ResSel.MEM_RES),
    #opcode_store
    0b0100011 : ControlSignals(mem_write=1, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_S),
    #opcode_imm_op
    0b0010011 : ControlSignals(reg_write=1, op_b_sel=OP_B_SEL.OP_B_IMM, imm_sel=ImmSel.IMM_I),
    #opcode_op
    0b0110011 : ControlSignals(reg_write=1),
    #opcode_misc_mem (fence = NOP in single-cycle)
    0b0001111 : ControlSignals(),
    #opcode_system (ecall/ebreak -> halt)
    0b1110011 : ControlSignals(halt=1),
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
            exp_control = opcode_to_control_sig[opcode]

            funct3 =  0 if funct3 == "x" else int(funct3, 2)
            funct7 =  0 if funct7 == "x" else int(funct7, 2)
            exp_alu_op = ALU_OP[exp_alu_op]

            dut.opcode_i.value = opcode
            dut.funct3.value = funct3
            dut.funct7.value = funct7

            await timer

            alu_op = ALU_OP(dut.alu_op_o.value)
            reg_write = int(dut.reg_write_o.value)
            mem_write = int(dut.mem_write_o.value)
            imm_sel = ImmSel(dut.imm_sel_o.value)
            op_b_sel = OP_B_SEL(dut.op_b_sel_o.value)
            op_a_sel = OP_A_SEL(dut.op_a_sel_o.value)
            res_sel = ResSel(dut.result_sel_o.value)
            branch = int(dut.branch_o.value)
            jump = int(dut.jump_o.value)
            halt = int(dut.halt_o.value)

            control = ControlSignals(
                reg_write=reg_write,
                mem_write=mem_write,
                op_a_sel=op_a_sel,
                op_b_sel=op_b_sel,
                alu_op=alu_op,
                halt=halt,
                branch=branch,
                jump=jump,
                result_sel=res_sel,
                imm_sel=imm_sel
            )

            # in this case the ALU_OP has to be checked against the text file
            if (opcode == 0b0010011 or opcode == 0b0110011) :
                control.alu_op = ALU_OP.ALU_ADD #force the alu to match the default as it is not set for the opcode_op and opcode_imm_op

            assert control == exp_control, f"\nEXPECTED CONTROL for command {mnemonic}\n\n {exp_control}, \n\n RECEIVED CONTROL : \n\n {control}"
            #match the alu_op separately against the hex file.
            assert alu_op == exp_alu_op, f"exp alu_op {exp_alu_op.name}, got {ALU_OP(alu_op).name}"


#every opcode outside the 11 legal ones must decode to halt
@cocotb.test()
async def test_illegal_opcodes(dut) :
    legal_opcodes = set(mnem_opcode_map.values())

    for opcode in range(128) :
        if opcode in legal_opcodes :
            continue

        dut.opcode_i.value = opcode
        dut.funct3.value = random.getrandbits(3)
        dut.funct7.value = random.getrandbits(7)

        await timer

        assert int(dut.halt_o.value) == 1, f"halt_o not asserted for illegal opcode {opcode:07b}"
        assert int(dut.reg_write_o.value) == 0, f"reg_write_o asserted for illegal opcode {opcode:07b}"
        assert int(dut.mem_write_o.value) == 0, f"mem_write_o asserted for illegal opcode {opcode:07b}"
            