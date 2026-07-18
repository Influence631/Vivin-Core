import random

with open("init_mem.txt", "w") as f :
    for i in range (1024):
        rand = random.randint(0, 0xFFFFFFFF)
        f.write(str((hex(rand)))[2:])
        f.write('\n')
