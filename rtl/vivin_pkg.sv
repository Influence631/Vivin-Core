`default_nettype none

package vivin_pkg;

  typedef enum logic [2:0] {
    IMM_I,
    IMM_S,
    IMM_B,
    IMM_U,
    IMM_J
  } imm_sel_e;

  typedef enum logic [6:0] {
    OPCODE_LOAD = 7'b0000011,
    OPCODE_STORE = 7'b0100011,
    OPCODE_BRANCH = 7'b1100011,
    OPCODE_OP_IMM = 7'b0010011,
    OPCODE_AUIPC = 7'b0010111,
    OPCODE_OP = 7'b0110011,
    OPCODE_LUI = 7'b0110111,
    OPCODE_JAL = 7'b1101111,
    OPCODE_JALR = 7'b1100111,
    OPCODE_SYSTEM = 7'b1110011,
    OPCODE_MISC_MEM = 7'b0001111
  } opcode_e;

  typedef enum logic [1:0] {
    ALU_ADD_OP, //force add because some instructions dont encode alu op, but use add.
    ALU_ELABORATE_R, // for register instructions to differentiate add / sub using funct7
    ALU_ELABORATE_IMM // for immediate instructions, funct 7 used to differentiate shifts
  } alu_op_hint_e ; //this is a hint for alu_decoder, provided by the main decoder along with funct3 and funct7
  
  typedef enum logic [1:0] {
    ALU_RES,
    MEM_RES,
    PC4_RES
  } result_sel_e;

  typedef enum logic [1:0] {
    OP_A_RS1, //normal
    OP_A_PC, //auipc, jal
    OP_A_ZERO //lui
  } op_a_sel_e;
  
  typedef enum logic {
    OP_B_RS2,
    OP_B_IMM
  } op_b_sel_e;
  
  typedef enum logic {
    PC4, //default
    PC_TARGET //jal, branch, jalr
  } pc_sel_e;

  typedef enum logic [3:0] {
    ALU_ADD = 4'd0,
    ALU_SUB = 4'd1,
    ALU_SLT = 4'd2,
    ALU_SLTU = 4'd3,
    ALU_AND = 4'd4,
    ALU_OR = 4'd5,
    ALU_XOR = 4'd6,
    ALU_SLL = 4'd7,
    ALU_SRL = 4'd8,
    ALU_SRA = 4'd9
  } alu_op_e;

  typedef enum logic [1:0] {
    BYTE = 2'b00,
    HALF = 2'b01,
    WORD = 2'b10
  } lsu_size_e;

endpackage
