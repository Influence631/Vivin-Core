`default_nettype none

package vivin_pkg;

  typedef enum logic [2:0] {
    ImmI,
    ImmS,
    ImmB,
    ImmU,
    ImmJ
  } imm_sel_e;

  typedef enum logic [6:0] {
    OPCODE_LOAD,
    OPCODE_STORE,
    OPCODE_BRANCH,
    OPCODE_OP_IMM,
    OPCODE_AUIPC,
    OPCODE_OP,
    OPCODE_LUI,
    OPCODE_JAL,
    OPCODE_JALR,
    OPCODE_SYSTEM,
    OPCODE_MISC_MEM
  } opcode_e;

endpackage
