`default_nettype none

module alu (
  input vivin_pkg::alu_op_e operator_i,
  input logic [31:0] operand_a_i,
  input logic [31:0] operand_b_i,
  
  output logic [31:0] result_o
);
  import vivin_pkg::*;

  logic [4:0] shamt;

  assign shamt = operand_b_i[4:0];

  always_comb begin 
    result_o = '0;
    unique case (operator_i)
      ALU_ADD : result_o = operand_a_i + operand_b_i;
      ALU_SUB : result_o = operand_a_i - operand_b_i;
      ALU_SLT : result_o = $signed(operand_a_i) < $signed(operand_b_i) ? 32'b1 : 32'b0;
      ALU_SLTU : result_o = operand_a_i < operand_b_i ? 32'b1 : 32'b0;
      ALU_AND : result_o = operand_a_i & operand_b_i;
      ALU_OR : result_o = operand_a_i | operand_b_i;
      ALU_XOR : result_o = operand_a_i ^ operand_b_i;
      ALU_SLL : result_o = operand_a_i << shamt;
      ALU_SRL : result_o = operand_a_i >> shamt;
      ALU_SRA : result_o = $signed(operand_a_i) >>> shamt; //make signed
      default : ;
    endcase
  end
endmodule