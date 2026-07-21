`default_nettype none

module imm_gen(
  input vivin_pkg::imm_sel_e imm_sel_i,
  input wire logic [31:7] instr_i,

  output logic [31:0] data_o
);
  import vivin_pkg::*;

  always_comb begin 
    unique case (imm_sel_i)
      ImmI : data_o = {{21{instr_i[31]}}, instr_i[30:25], instr_i[24:21], instr_i[20]};
      ImmS : data_o = {{21{instr_i[31]}}, instr_i[30:25], instr_i[11:8], instr_i[7]};
      ImmB : data_o = {{20{instr_i[31]}}, instr_i[7], instr_i[30:25], instr_i[11:8], 1'b0};
      ImmU : data_o = {instr_i[31], instr_i[30:20], instr_i[19:12], 12'b0};
      ImmJ : data_o = {{12{instr_i[31]}}, instr_i[19:12], instr_i[20], instr_i[30:25], instr_i[24:21],1'b0};
      default : data_o = '0;
    endcase
  end

endmodule 
