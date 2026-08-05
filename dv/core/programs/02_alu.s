addi x1, x0, 0xF
slti x2, x0, 1
slti x2, x1, 1
sltiu x3, x2, 0xA
sltiu x3, x0, 0xA
xori x4, x1, -273   # 0xEEF
xori x4, x0, -273
ori x5, x2, -594    # 0xDAE
ori x5, x0, -594
andi x6, x0, -774  # 0xCFA
andi x6, x1, -774
slli x7, x0, 2
slli x7, x1, 2
srli x8, x0, 1
srli x8, x1, 1
srai x9, x0, 0
srai x9, x1, 0
sub x31, x0, x1
done:
    jal    x0, done
