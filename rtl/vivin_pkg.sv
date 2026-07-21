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

  typedef enum logic {
    OP_B_REG_B,
    OP_B_IMM
  } op_b_sel_e;
  
endpackage
