addi x1, x0, 255
addi x2, x0, -255
addi x3, x0, 0
addi x4, x0, 255

#x1==x2 -> taken : not_taken
#x1!=x2 -> not_taken -> taken
beq x1, x2, taken
not_taken:
    bne x1, x2, taken
    jal x0, not_taken
taken:
    blt x1, x0, error
    blt x1,x2, error
    bltu x1, x2, correct
    


error:
    li x5, 0xDEADBEEF
    jal x0,error

correct:
    li x5, 0x10101010
    sw x5, 0(x0)
    bge x2, x1, error
    bgeu x2,x1, done
    jal x0, error

done :
    fence
    jal x0, done