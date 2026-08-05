#populate the registers
addi x1,x0,15
addi x2,x0,255
addi x3,x0,-1
addi x4,x0,-128 

#now test stores sw rs2, offset(rs1)
sw x1, 0(x0) #write full reg 1 into memory address 0
sb x1, 3(x0) #write reg1[7:0] into mem addr 0

#test reading from memory #ld rd, offset(rs1)
lw x1, 0(x0)
lh x1, 2(x0)
lb x1, 3(x0)

#store -128 in address 15
sw x4, 1(x1)
lh x31, 3(x1)


done:
    jal x0,done