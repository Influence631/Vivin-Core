`default_nettype none

module load_store_unit (
  //funct3 {unsigned, size} : BYTE, HW, W
  input vivin_pkg::lsu_size_e size_i,

  input wire logic is_signed_i,
  
  input wire logic [31:0] addr_i, //contains the address of loads/stores
  
  //loads
  input wire logic is_load_i,
  
  input wire logic [31:0] mem_rdata_i,
  output logic [31:0] load_rdata_o,
  //stores
  input wire logic is_store_i,
  
  input wire logic [31:0] store_wdata_i,
  output logic [31:0] mem_wdata_o,

  ///
  output logic mem_we_o,
  output logic [3:0] mem_be_o,
  
  output logic fault_o
);
  import vivin_pkg::*;

  logic misaligned;

  logic [1:0] offset;
  assign offset = addr_i[1:0];

  assign fault_o = (is_load_i | is_store_i) & misaligned;
  assign mem_write_o = is_store_i & (~misaligned);

  always_comb begin 
    misaligned = 1'b0;
    mem_be_o = '0;
    unique case (size_i)
      BYTE : begin 
        unique case (offset)
          2'b00 : mem_be_o = 4'b0001;
          2'b01 : mem_be_o = 4'b0010;
          2'b10 : mem_be_o = 4'b0100;
          2'b11 : mem_be_o = 4'b1000;
          default : ;
        endcase 
      end
      HALF : begin 
        unique case (offset)
          2'b00 : mem_be_o = 4'b0011;
          2'b10 : mem_be_o = 4'b1100;
          default : misaligned = 1'b1;
        endcase
      end
      WORD : begin 
        unique case (offset) 
          2'b00 : mem_be_o = 4'b1111;;
          default : misaligned = 1'b1;;
        endcase
      end
      default : ;
    endcase
  end

endmodule