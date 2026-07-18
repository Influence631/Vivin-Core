`default_nettype none

module memory #(
  parameter int unsigned Depth = 1024,
  localparam int unsigned Aw = $clog2(Depth),
  parameter string MemInitFile = ""
) (

  input wire logic clk_i,
  input wire logic w_en_i,
  input wire logic [3:0] be_i,

  input wire logic [Aw-1:0] addr_i,
  input wire logic [31:0] data_i,

  output logic [31:0] data_o
);
  //assert in the lsu
  //always_comb assert (addr_i[1:0] == 2'b00);
  
  logic [31:0] mem [Depth];


  initial begin 
    if (MemInitFile != "") $readmemh(MemInitFile, mem);
  end

  always_ff @(posedge clk_i) begin 
    if (w_en_i) begin 
      for (int i = 0; i < 4; i++) begin 
        if (be_i[i]) begin
          mem[addr_i][(i * 8)+:8] <= data_i[(i*8)+:8];
        end
      end
    end
  end

  assign data_o = mem[addr_i];

endmodule
