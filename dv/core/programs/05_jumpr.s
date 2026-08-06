#populate the registers
addi x1,x0,16
addi x2,x0,-1
addi x5, x0, 1


#x4 <- pc + 4
#pc <- test_reg
la x3, test_reg
jalr x4, x3, 0 #jump to the test_reg block and save the return addres into x4 

#nops so that pc_target != pc+4 
nop
nop
nop

jal x0, done

test_reg :
    add x3, x1, x2
    sub x3, x1, x2
    sll x3, x1, x1
    slt x3, x1, x2
    sltu x3, x1, x2
    xor x3, x1, x2
    or x3, x1, x2
    and x3, x1, x2
    srl x3, x1, x5

    lui x3, 0x80000
    add x1, x1, x3
    sra x3, x1, x5
    
    #return to nops
    jalr x0, x4, 0 

done :
    jal x0, done