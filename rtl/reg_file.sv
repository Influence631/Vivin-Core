`default_nettype none

module reg_file (
    //control signals#
    input wire logic clk_i,
    input wire logic rst_ni,  //reset all registers to '0
    input wire logic w_en_i,

    //read ports
    input  wire logic [4:0] r1_addr_i,
    input  wire logic [4:0] r2_addr_i,
    output logic [31:0] r1_data_o,
    output logic [31:0] r2_data_o,

    //write port
    input wire logic [4:0] w_addr_i,
    input wire logic [31:0] w_data_i
);

  logic [31:0] regfile [32];


  assign r1_data_o = r1_addr_i == 5'd0 ? '0 : regfile[r1_addr_i];
  assign r2_data_o = r2_addr_i == 5'd0 ? '0 : regfile[r2_addr_i];

  always_ff @(posedge clk_i) begin
    if (!rst_ni) begin
      for (int i = 0; i < 32; i++) begin
        regfile[i] <= '0;
      end
    end else begin
      if (w_en_i && w_addr_i != 5'd0) regfile[w_addr_i] <= w_data_i;
    end
  end

endmodule
