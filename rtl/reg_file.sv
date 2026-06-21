`default_nettype none

module reg_file (
    //control signals#
    input logic clk_i,
    input logic rst_ni,  //reset all registers to '0
    input logic w_en_i,

    //read ports
    input  logic [4:0] r1_addr_i,
    input  logic [4:0] r2_addr_i,
    output logic [31:0] r1_data_o,
    output logic [31:0] r2_data_o,

    //write port
    input logic [4:0] w_addr_i,
    input logic [31:0] w_data_i
);

  logic [31:0] regfile [32];


  assign r1_data_o = regfile[r1_addr_i];
  assign r2_data_o = regfile[r2_addr_i];

  always_comb begin

  end

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      for (int i = 0; i < 32; i++) begin
        regfile[i] <= '0;
      end
    end else begin
      if (w_en_i) regfile[w_addr_i] <= w_data_i;
      regfile[0] <= '0;
    end
  end

endmodule
