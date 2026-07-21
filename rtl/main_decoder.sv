`default_nettype none

module main_decoder (
  input wire logic [31:0] instr_i,
  input wire logic [31:0] alu_result, 
  
  output logic is_zero, //zero flag
  
  //control signals
  output vivin_pkg::imm_sel_e imm_sel_o,
  output vivin_pkg::op_b_sel_e op_b_sel_o,
);
  import vivin_pkg::*; 

  logic [1:0] alu_hint;
  opcode_e opcode;
  //this module will instantiate alu decoder, pass alu op hint to it from the instruction opcode
  //this unit also sets all the Controll signals needed.
  //use automatic functions for cleaner code
endmodule