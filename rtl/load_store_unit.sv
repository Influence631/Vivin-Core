`default_nettype none

module load_store_unit (
  input vivin_pkg::lsu_size_e size_i,
  input wire logic is_signed_i,
  input wire logic [1:0] addr_offset_i,
  
  input wire logic [31:0] mem_rdata_i,
  input wire logic [31:0] store_wdata_i,

  output logic [31:0] load_rdata_o,
  output logic [31:0] mem_wdata_o,

  output logic [3:0] mem_be_o,  
  output logic misaligned_o
);
  import vivin_pkg::*;

  logic [31:0] shifted;
  
  assign mem_wdata_o = store_wdata_i << {addr_offset_i, 3'b000};
  
  // handle stores + misalignment
  always_comb begin 
    misaligned_o = 1'b0;
    mem_be_o = '0;
    
    unique case (size_i)
      BYTE : begin 
        unique case (addr_offset_i)
          2'b00 : mem_be_o = 4'b0001;
          2'b01 : mem_be_o = 4'b0010;
          2'b10 : mem_be_o = 4'b0100;
          2'b11 : mem_be_o = 4'b1000;
          default : ;
        endcase 
      end
      HALF : begin 
        unique case (addr_offset_i)
          2'b00 : mem_be_o = 4'b0011;
          2'b10 : mem_be_o = 4'b1100;
          default : misaligned_o = 1'b1;
        endcase
      end
      WORD : begin 
        unique case (addr_offset_i) 
          2'b00 : mem_be_o = 4'b1111;
          default : misaligned_o = 1'b1;
        endcase
      end
      default : ;
    endcase
  end

  assign shifted = mem_rdata_i >> {addr_offset_i, 3'b000}; //same as offset * 8
  
  //set the filling bit for both signed and unsigned to be the msb of the requested bytes
  
  always_comb begin
    load_rdata_o = '0;
  
    unique case (size_i)
      BYTE : load_rdata_o = {{24{is_signed_i & shifted[7]}}, shifted[7:0]};
      HALF : load_rdata_o = {{16{is_signed_i & shifted[15]}}, shifted[15:0]};
      WORD : load_rdata_o = shifted; // unchanged
      default : ;
    endcase
  end 
endmodule