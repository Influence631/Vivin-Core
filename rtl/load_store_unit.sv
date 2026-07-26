`default_nettype none

//i still need to figure out the semantics for this one,
//but it will handle the readings from memory writings to regfile 
module load_store_unit (
  input wire logic [31:0] alu_res_i,
  input wire logic mem_write_i,
  input wire logic reg_write_i,

);

endmodule