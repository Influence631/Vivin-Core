`default_nettype none

//next :
//1. finish the datapath for lw, branches, alu decoder, build lsu
// make ports branch, jump, halt for the top level to be able to set the pc_next with pc_redirect
module main_decoder (
  input vivin_pkg::opcode_e opcode_i,
  input wire logic [2:0] funct3,
  input wire logic [6:0] funct7,
  
  //control signals
  output vivin_pkg::imm_sel_e imm_sel_o,
  output vivin_pkg::op_a_sel_e op_a_sel_o, 
  output vivin_pkg::op_b_sel_e op_b_sel_o,
  output vivin_pkg::alu_op_e alu_op_o,
  output vivin_pkg::result_sel_e result_sel_o,
  
  output logic reg_write_o,
  output logic mem_write_o,
  
  output logic halt_o,
  output logic branch_o,
  output logic jump_o
);
  import vivin_pkg::*; 

  alu_op_hint_e alu_op_hint;

  // decode instructions 
  always_comb begin
    imm_sel_o = IMM_I;
    mem_write_o = 1'b0;
    reg_write_o = 1'b0;
    branch_o = 1'b0;
    jump_o = 1'b0;
    halt_o = 1'b0;

    result_sel_o = ALU_RES;
    op_a_sel_o = OP_A_RS1;
    op_b_sel_o = OP_B_RS2;

    alu_op_hint = ALU_ADD_OP;
  
    unique case (opcode_i)
      OPCODE_LOAD : begin 
        alu_op_hint = ALU_ADD_OP;

        reg_write_o = 1'b1;
        result_sel_o = MEM_RES;

        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_I;
      end
      OPCODE_STORE : begin 
        alu_op_hint = ALU_ADD_OP;

        mem_write_o = 1'b1;
        
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_S;
      end
      OPCODE_BRANCH : begin 
        alu_op_hint = ALU_ADD_OP; // alu performs the target calculation, while the comparator outputs the result
        
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_B;

        branch_o = 1'b1;
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
      end
      OPCODE_MISC_MEM : begin //fence
        //here can later expand to support fence and zicsr instructions,
        //but currently this default to a NOP, which is fine for single-cycle.
      end
      OPCODE_SYSTEM : begin
        halt_o = 1'b1;
        //halt on ecall and ebreak by not driving the pc, controlled by the halt_o;
      end
      default : ;
    endcase
  end


  alu_decoder alu_decoder_u(
    .alu_op_hint_i(alu_op_hint),
    .funct3(funct3),
    .funct7(funct7),
    .alu_op_o(alu_op_o)
  );
endmodule