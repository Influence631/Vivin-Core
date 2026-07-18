`default_nettype none

module memory #(
  parameter int unsigned Depth = 1024,
  localparam int unsigned Aw = $clog2(Depth),
  parameter string MemInitFile = ""
) (

  input wire logic clk_i,
  input wire logic we_i,
  input wire logic [3:0] be_i,

  input wire logic [Aw+1:0] addr_i, //byte address.
  input wire logic [31:0] data_i,

  output logic [31:0] data_o
);
  
  logic _unused;
  assign _unused = ^addr_i[1:0]; //the address is byte addressable, but lowest 2 bits are unused. this removes lint warning.

  logic [31:0] mem [Depth];


  initial begin 
    if (MemInitFile != "") $readmemh(MemInitFile, mem);
  end

  always_ff @(posedge clk_i) begin 
    if (we_i) begin
      if (addr_i[1:0] != 2'b00) begin 
        $fatal(1, "STOPPING EXECUTION, WRITING TO MISALIGNED ADDRESS %h", addr_i);
      end else begin
        for (int i = 0; i < 4; i++) begin 
          if (be_i[i]) begin
            mem[addr_i[Aw+1:2]][(i * 8)+:8] <= data_i[(i*8)+:8];
          end
        end
      end
    end
  end

  assign data_o = mem[addr_i[Aw+1:2]];

endmodule
