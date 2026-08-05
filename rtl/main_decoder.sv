`default_nettype none

//next :
//1. finish the datapath for lw, branches, alu decoder, build lsu
// make ports branch, jump, halt for the top level to be able to set the pc_next with pc_redirect
module main_decoder (
  input vivin_pkg::opcode_e opcode_i,
  input wire logic [2:0] funct3_i,
  input wire logic [6:0] funct7_i,
  
  //control signals
  output vivin_pkg::imm_sel_e imm_sel_o,
  output vivin_pkg::op_a_sel_e op_a_sel_o, 
  output vivin_pkg::op_b_sel_e op_b_sel_o,
  output vivin_pkg::alu_op_e alu_op_o,
  output vivin_pkg::result_sel_e result_sel_o,
  output logic reg_write_o,
  
  output logic sys_halt_o,
  output logic illegal_instr_o,
  output logic branch_o,
  output logic jump_o,
  output logic is_load_o,
  output logic is_store_o
);
  import vivin_pkg::*; 

  alu_op_hint_e alu_op_hint;

  logic illegal_alu_funct, illegal_opcode, illegal_funct;

  assign illegal_instr_o = illegal_alu_funct | illegal_funct | illegal_opcode; 
  // decode instructions 
  always_comb begin
    imm_sel_o = IMM_I;
    reg_write_o = 1'b0;
    
    {branch_o, jump_o, is_load_o, is_store_o} = 'b0;
    
    result_sel_o = ALU_RES;
    op_a_sel_o = OP_A_RS1;
    op_b_sel_o = OP_B_RS2;

    alu_op_hint = ALU_ADD_OP;
    
    {illegal_opcode, illegal_funct, sys_halt_o} = 'b0;
  
    unique case (opcode_i)
      OPCODE_LOAD : begin 
        alu_op_hint = ALU_ADD_OP;

        reg_write_o = 1'b1;
        result_sel_o = MEM_RES;

        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_I;

        is_load_o = 1'b1; 
        illegal_funct = (funct3_i inside {3'b011, 3'b110, 3'b111});
      end
      OPCODE_STORE : begin 
        alu_op_hint = ALU_ADD_OP;
        
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_S;

        is_store_o = 1'b1;
        illegal_funct = !(funct3_i inside {3'b000, 3'b001, 3'b010});
      end
      OPCODE_BRANCH : begin 
        alu_op_hint = ALU_ADD_OP; // alu performs the target calculation, while the comparator outputs the result
        
        op_a_sel_o = OP_A_PC;
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_B;

        branch_o = 1'b1;
        illegal_funct = (funct3_i inside {3'b010, 3'b011});
      end
      OPCODE_OP_IMM : begin 
        alu_op_hint = ALU_ELABORATE_IMM;
        
        reg_write_o = 1'b1;
        result_sel_o = ALU_RES;

        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_I;
      end
      OPCODE_LUI : begin
        alu_op_hint = ALU_ADD_OP;

        reg_write_o = 1'b1;
        result_sel_o = ALU_RES;

        op_a_sel_o = OP_A_ZERO;
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_U;
      end
      OPCODE_AUIPC : begin 
        alu_op_hint = ALU_ADD_OP;

        reg_write_o = 1'b1;
        result_sel_o = ALU_RES; 

        op_a_sel_o = OP_A_PC;
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_U;
      end
      OPCODE_OP : begin
        alu_op_hint = ALU_ELABORATE_R;

        reg_write_o = 1'b1;
        result_sel_o = ALU_RES;
      end
      OPCODE_JAL : begin 
        alu_op_hint = ALU_ADD_OP;

        reg_write_o = 1'b1;
        result_sel_o = PC4_RES;
        
        op_a_sel_o = OP_A_PC;  // the JAL passes PC as reg A
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_J;

        jump_o = 1'b1;
      end
      OPCODE_JALR : begin
        alu_op_hint = ALU_ADD_OP;

        reg_write_o = 1'b1;
        result_sel_o = PC4_RES;

        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_I;

        jump_o = 1'b1;
        illegal_funct = !(funct3_i == 3'b000); 
      end
      OPCODE_MISC_MEM : begin //fence
        //here can later expand to support fence and zicsr instructions,
        //but currently this default to a NOP, which is fine for single-cycle.
        illegal_funct = !(funct3_i == 3'b000);
      end
      OPCODE_SYSTEM : begin
        illegal_funct = !(funct3_i == 3'b000);
        sys_halt_o = 1'b1;
        //halt on ecall and ebreak by not driving the pc, controlled by the decoder_halt_o;
      end
      default : illegal_opcode = 1'b1; 
    endcase
  end

  alu_decoder alu_decoder_u(
    .alu_op_hint_i(alu_op_hint),
    .funct3_i(funct3_i),
    .funct7_i(funct7_i),
    .alu_op_o(alu_op_o),
    .illegal_funct_o(illegal_alu_funct)
  );
endmodule