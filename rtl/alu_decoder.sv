`default_nettype none

module alu_decoder (
  input vivin_pkg::alu_op_hint_e alu_op_hint_i,
  input wire logic [2:0] funct3_i,
  input wire logic [6:0] funct7_i,

  output vivin_pkg::alu_op_e alu_op_o,
  output logic illegal_funct_o
);
  import vivin_pkg::*;

  function automatic alu_op_e decode_arith(logic is_reg, logic [2:0] funct3, logic funct7_5);
    unique case (funct3)
      3'b000 : return (is_reg && funct7_5) ? ALU_SUB : ALU_ADD;
      3'b001 : return ALU_SLL;
      3'b010 : return ALU_SLT;
      3'b011 : return ALU_SLTU;
      3'b100 : return ALU_XOR;
      3'b101 : return funct7_5 ? ALU_SRA : ALU_SRL;
      3'b110 : return ALU_OR;
      3'b111 : return ALU_AND; 
    default: return ALU_ADD;
    endcase
  endfunction
  
  function automatic logic funct7_legal(is_reg, logic [2:0] funct3, logic [6:0] funct7);
    unique case (funct3)
      3'b000: return is_reg ? (funct7 inside {7'b0100000, 7'b0000000}) : 1'b1;
      3'b001 : return funct7 == 7'b0000000;
      3'b101 : return (funct7 inside {7'b0100000, 7'b0000000});
      default : return is_reg ? (funct7 == 7'b0000000) : 1'b1;
    endcase
  endfunction

  always_comb begin
    alu_op_o = ALU_ADD;
    illegal_funct_o = 1'b0;

    unique case (alu_op_hint_i)
      ALU_ADD_OP : alu_op_o = ALU_ADD;
      ALU_ELABORATE_R : begin 
        alu_op_o = decode_arith(1'b1, funct3_i, funct7_i[5]);
        illegal_funct_o = !funct7_legal(1'b1, funct3_i, funct7_i);
      end
      ALU_ELABORATE_IMM : begin
        alu_op_o = decode_arith(1'b0, funct3_i, funct7_i[5]);
        illegal_funct_o = !funct7_legal(1'b0, funct3_i, funct7_i);
      end
    default: ;
    endcase
  end

endmodule