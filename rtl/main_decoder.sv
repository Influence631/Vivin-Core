`default_nettype none

module main_decoder (
  input opcode_e opcode,
  input wire logic [2:0] func3,
  input wire logic [6:0] func7,
  input wire logic alu_zero, //is_zero flag 
  
  //control signals
  output vivin_pkg::imm_sel_e imm_sel_o,
  output vivin_pkg::op_b_sel_e op_b_sel_o,
  output vivin_pkg::alu_op_e alu_control_o,
  output vivin_pkg::pc_sel_e pc_sel_o,
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

  always_comb begin
    imm_sel_o = IMM_I;
    mem_write_o = 1'b0;
    reg_write_o = 1'b0;
    pc_sel_o = PC4;
    result_sel_o = ALU_RES;
    alu_op_hint = ALU_ADD_OP;
    branch = 1'b0;
    //jal = 1'b0;

    unique case (opcode)
      OPCODE_LOAD : begin 
        alu_op_hint = ALU_ADD_OP;
        reg_write_o = 1'b1;
        result_sel_o = ALU_RES;
      end
      OPCODE_STORE : begin 
        alu_op_hint = ALU_ADD_OP;
      end
      OPCODE_BRANCH : begin 
        alu_op_hint = ALU_BRANCH_OP;
        branch = 1'b1;
      end
      OPCODE_OP_IMM : begin 
        alu_op_hint = ALU_ELABORATE_IMM;
      end
      OPCODE_AUIPC : begin 
        alu_op_hint = ALU_ADD_OP;
      end
      OPCODE_OP : begin 
        alu_op_hint = ALU_ELABORATE_R;
      end
      OPCODE_LUI : begin 
        alu_op_hint = ALU_ADD_OP;
      end
      OPCODE_JAL : begin 
        alu_op_hint = ALU_ADD_OP;
      end
      OPCODE_JALR : begin 
        alu_op_hint = ALU_ADD_OP;
      end
      OPCODE_SYSTEM : begin 
        //alu_op_hint = ALU_ADD_OP
        //defaults to NOP atm, but need to add halt for ecall and ebreak
      end
      OPCODE_MISC_MEM : begin 
        //alu_op_hint = ALU_ADD_OP
        //this defaults to NOP, but later can add zicsr extension.
      end
      default : ;
    endcase
  end


  alu_decoder alu_decoder_u(
    .alu_op_hint_i(alu_op_hint),
    .func3(func3),
    .func7(func7),
    .alu_op_o(alu_control_o)
  );



endmodule