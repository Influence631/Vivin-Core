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
  output vivin_pkg::alu_op_e alu_control_o,
  output vivin_pkg::result_sel_e result_sel_o,
  output logic reg_write_o,
  output logic mem_write_o
);
  import vivin_pkg::*; 


  alu_op_hint_e alu_op_hint;
  logic branch;
  logic jal;
  //this module will instantiate alu decoder, pass alu op hint to it from the instruction opcode
  //this unit also sets all the Controll signals needed.
  //use automatic functions for cleaner code

  //todo:
  //1.  define the sources of immgen
  //2. define all the result sources
  //3. reinterpret branch results 
  //4. only the pc sel is runtime dependant, the rest are static.

  //1. decode instructions 
  always_comb begin
    imm_sel_o = IMM_I;
    mem_write_o = 1'b0;
    reg_write_o = 1'b0;
    branch = 1'b0;

    op_a_sel_o = OP_A_RS1;
    op_b_sel_o = OP_B_RS2;

    alu_op_hint = ALU_ADD_OP;
  
    //jal = 1'b0;

    unique case (opcode_i)
      OPCODE_LOAD : begin 
        alu_op_hint = ALU_ADD_OP;
        reg_write_o = 1'b1;
        op_b_sel_o = OP_B_IMM;
        //result_sel_o = MEM_RES;
      end
      OPCODE_STORE : begin 
        alu_op_hint = ALU_ADD_OP;
        mem_write_o = 1'b1;
        op_b_sel_o = OP_B_IMM;
      end
      OPCODE_BRANCH : begin 
        alu_op_hint = ALU_BRANCH_OP;
        branch = 1'b1;
        op_b_sel_o = OP_B_IMM;
        imm_sel_o = IMM_B;
      end
      OPCODE_OP_IMM : begin 
        alu_op_hint = ALU_ELABORATE_IMM;
        op_b_sel_o = OP_B_IMM;
      end
      OPCODE_AUIPC : begin 
        alu_op_hint = ALU_ADD_OP;
        op_a_sel_o = OP_A_PC;
        op_b_sel_o = OP_B_IMM;

        //imm_sel_o = IMM
      end
      OPCODE_OP : begin
        alu_op_hint = ALU_ELABORATE_R;
        reg_write_o = 1'b1;
        op_b_sel_o = OP_B_RS2;
      end
      OPCODE_LUI : begin
        alu_op_hint = ALU_ADD_OP;
        reg_write_o = 1'b1;
        op_a_sel_o = OP_A_ZERO;
        op_b_sel_o = OP_B_IMM;
      end
      OPCODE_JAL : begin 
        alu_op_hint = ALU_ADD_OP;
        reg_write_o = 1'b1;
        //result_sel_o = ALU_RES; // the JAL passes PC as reg A
        op_a_sel_o = OP_A_PC;
      end
      OPCODE_JALR : begin
        alu_op_hint = ALU_ADD_OP;
        //pc_sel_o = PC_JALR;
        op_b_sel_o = OP_B_IMM;
        reg_write_o = 1'b1;
        //result_sel_o = PC4_RES;
      end
      // OPCODE_SYSTEM : begin 
      //   //alu_op_hint = ALU_ADD_OP
      //   //defaults to NOP atm, but need to add halt for ecall and ebreak
      // end
      // OPCODE_MISC_MEM : begin 
      //   //alu_op_hint = ALU_ADD_OP
      //   //this defaults to NOP, but later can add zicsr extension.
      // end
      default : ;
    endcase
  end


  alu_decoder alu_decoder_u(
    .alu_op_hint_i(alu_op_hint),
    .funct3(funct3),
    .funct7(funct7),
    .alu_op_o(alu_control_o)
  );
endmodule