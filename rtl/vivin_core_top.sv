`default_nettype none

module vivin_core_top (
  input wire logic clk_i,
  input wire logic rst_ni
);
  import vivin_pkg::*;
  localparam int unsigned MemDepth = 1024;
  localparam int unsigned Aw = $clog2(MemDepth);

  logic [31:0] pc, pc_4, pc_target;
  logic [31:0] pc_next;
  
  logic branch, jump, load, store;
  logic taken;
  logic redirect;

  logic [31:0] instr;
  opcode_e opcode;
  logic [2:0] funct3;
  logic [6:0] funct7;

  imm_sel_e imm_sel;
  result_sel_e result_sel;
  op_a_sel_e op_a_sel;
  op_b_sel_e op_b_sel;
  alu_op_e alu_op;
  
  logic decoder_reg_we; // this needs some gating for halts / misalligned
  logic reg_we;
  logic mem_we;

  logic decoder_halt;
  logic lsu_misaligned;
  logic halt;
  logic misaligned_store;
  logic misaligned_load;
  logic pc_misaligned;

  logic [31:0] op_a, op_b;
  logic [31:0] rs1_data, rs2_data;
  logic [31:0] mem_wdata;
  logic [31:0] alu_result;
  logic [31:0] result;
  logic [3:0] be;
  logic [31:0] mem_rdata;
  logic [31:0] mem_result;
  logic [31:0] imm;

  logic [4:0] rd, rs1, rs2;
  assign rd = instr[11:7];
  assign rs1 = instr[19:15];
  assign rs2 = instr[24:20];

  assign redirect = (branch & taken) || jump;
  assign halt = decoder_halt || ((load | store) & lsu_misaligned) || pc_misaligned;

  assign misaligned_load = load & lsu_misaligned;
  assign misaligned_store = store & lsu_misaligned;
  assign pc_misaligned = redirect & pc_target[1];

  assign reg_we = decoder_reg_we & ~misaligned_load & ~halt; //gate regwrite on a misaligned load or halt
  assign mem_we = store & ~misaligned_store & ~halt; //gate memwrite on a misaligned store or halt
  
  assign pc_4 = pc + 32'd4;
  assign pc_target = redirect ? {alu_result[31:1], 1'b0} : '0;

  assign opcode = opcode_e'(instr[6:0]);
  assign funct3 = instr[14:12];
  assign funct7 = instr[31:25];

  always_comb begin
    unique case (op_a_sel)
      OP_A_RS1 : op_a = rs1_data;
      OP_A_PC : op_a = pc;
      OP_A_ZERO : op_a = '0;
      default : op_a = '0;
    endcase
  end

  always_comb begin 
    unique case (op_b_sel)
      OP_B_IMM : op_b = imm;
      OP_B_RS2 : op_b = rs2_data;
      default : ;
    endcase
  end

  always_comb begin 
    result = alu_result;
    unique case (result_sel)
      ALU_RES : result = alu_result;
      MEM_RES : result = mem_result;
      PC4_RES : result = pc_4;
      default : ;
    endcase
  end

  always_comb begin 
    pc_next = halt ? pc : (redirect ? pc_target : pc_4);
  end

  always_ff @(posedge clk_i) begin 
    if (!rst_ni) pc <= '0;
    else begin
      pc <= pc_next; //on a halt, loop pc should not increment.
    end 
  end
  
  main_decoder decoder_u (
    .opcode_i(opcode),
    .funct3_i(funct3),
    .funct7_i(funct7),
    .imm_sel_o(imm_sel),
    .op_a_sel_o(op_a_sel), 
    .op_b_sel_o(op_b_sel),
    .alu_op_o(alu_op),
    .result_sel_o(result_sel),
    .reg_write_o(decoder_reg_we),
    .decoder_halt_o(decoder_halt),
    .branch_o(branch),
    .jump_o(jump),
    .is_load_o(load),
    .is_store_o(store)
  );

  memory #(
    .Depth(MemDepth),
    .MemInitFile("dmemory.hex")
  )  data_mem_u (
    .clk_i(clk_i),
    .we_i(mem_we),
    .be_i(be),
    .addr_i(alu_result[Aw+1:0]),
    .data_i(mem_wdata),
    .data_o(mem_rdata)
  );

  memory #(
    .Depth(MemDepth),
    .MemInitFile("imemory.hex")
  ) instr_mem_u (
    .clk_i(clk_i),
    .we_i('0),
    .be_i('0),
    .addr_i(pc[Aw+1:0]),
    .data_i('0),
    .data_o(instr)
  );

  reg_file regfile_u (
    .clk_i(clk_i),
    .rst_ni(rst_ni),
    .w_en_i(reg_we),
    .r1_addr_i(rs1),
    .r2_addr_i(rs2),
    .w_addr_i(rd),
    .w_data_i(result),
    .r1_data_o(rs1_data),
    .r2_data_o(rs2_data)
  );

  imm_gen imm_gen_u (
    .imm_sel_i(imm_sel),
    .instr_i(instr[31:7]),
    .data_o(imm)
  ); 

  load_store_unit lsu_u (
    .size_i(lsu_size_e'(funct3[1:0])),
    .is_signed_i(funct3[2]),
    .addr_offset_i(alu_result[1:0]),
    .mem_rdata_i(mem_rdata),
    .store_wdata_i(rs2_data),
    .load_rdata_o(mem_result),
    .mem_wdata_o(mem_wdata),
    .mem_be_o(be),  
    .misaligned_o(lsu_misaligned)
  );

  branch_comparator branch_comp_u (
    .funct3_i(funct3),
    .rs1_data_i(rs1_data),
    .rs2_data_i(rs2_data),
    .taken_o(taken)
  );

  alu alu_u (
    .operator_i(alu_op),
    .operand_a_i(op_a),
    .operand_b_i(op_b),
    .result_o(alu_result)
  );

endmodule