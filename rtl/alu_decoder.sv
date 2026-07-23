`default_nettype none

module alu_decoder (
  input vivin_pkg::alu_op_hint_e alu_op_hint_i,
  input logic [2:0] func3,
  input logic [6:0] func7,

  output vivin_pkg::alu_op_e alu_op_o
);
  import vivin_pkg::*;

  function automatic alu_op_e decode_branch (func3_b_e funct3);
    unique case (funct3)
      BEQ : return ALU_SUB;
      BNE : return ALU_SUB;
      BLT : return ALU_SLT;
      BLTU : return ALU_SLTU;
      BGE : return ALU_SLT;
      BGEU : return ALU_SLTU;
      default : return ALU_SUB;
    endcase
  endfunction

  function automatic alu_op_e decode_arith(logic is_reg, logic [2:0] funct3, logic[6:0] funct7);
    unique case (funct3)
      3'b000 : return (is_reg && funct7[5]) ? ALU_SUB : ALU_ADD;
      3'b001 : return ALU_SLL;
      3'b010 : return ALU_SLT;
      3'b011 : return ALU_SLTU;
      3'b100 : return ALU_XOR;
      3'b101 : return funct7[5] ? ALU_SRA : ALU_SRL;
      3'b110 : return ALU_OR;
      3'b111 : return ALU_AND; 
    default: return ALU_ADD;
    endcase
  endfunction
  

  always_comb begin
    alu_op_o = ALU_ADD;
    unique case (alu_op_hint_i)
      ALU_ADD_OP : alu_op_o = ALU_ADD;
      ALU_BRANCH_OP : alu_op_o = decode_branch(func3_b_e'(func3));
      ALU_ELABORATE_R : alu_op_o = decode_arith(1'b1, func3, func7);
      ALU_ELABORATE_IMM : alu_op_o = decode_arith(1'b0, func3, func7);
    default: ;
    endcase
  end

endmodule