`default_nettype none

module branch_comparator (
  input wire logic [2:0] funct3_i,
  input wire logic [31:0] rs1_data_i, 
  input wire logic [31:0] rs2_data_i,

  output logic taken_o
);

  typedef enum logic [2:0] {
    BEQ = 3'b000,
    BNE = 3'b001,
    BLT = 3'b100,
    BGE = 3'b101,
    BLTU = 3'b110,
    BGEU = 3'b111
  } funct3_b_e;

  logic signed [31:0] rs1_signed, rs2_signed;
  
  assign rs1_signed = $signed(rs1_data_i);
  assign rs2_signed = $signed(rs2_data_i);

  always_comb begin 
    taken_o = 1'b0;
    unique case (funct3_b_e'(funct3_i))
      BEQ : taken_o = (rs1_data_i == rs2_data_i);
      BNE : taken_o = (rs1_data_i != rs2_data_i);
      BLT : taken_o = (rs1_signed < rs2_signed);
      BGE : taken_o = !(rs1_signed < rs2_signed);
      BLTU : taken_o = (rs1_data_i < rs2_data_i);
      BGEU : taken_o = !(rs1_data_i < rs2_data_i);
      default : ;
    endcase
  end

endmodule