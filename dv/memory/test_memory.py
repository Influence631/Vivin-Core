import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
import random
import logging

log = logging.getLogger("tb.memory")
log.setLevel(logging.INFO)

model = {}
numWords = 1024
init_path = "init_mem.hex"

def apply_be(old, new, byte_mask) :
    result = 0
    for i in range(4) :
        shift = i * 8
        if((byte_mask >> i) & 1) :
            result |= new & (0xFF << shift)
        else :
            result |= old & (0xFF << shift)

    return result

async def check_init(dut) :
    with open(init_path, "r") as file:    
        for index, value in enumerate (file) : 
            
            await RisingEdge(dut.clk_i)
            index *= 4 #convert word -> byte address
            dut.addr_i.value = index
            await ReadOnly()

            expected = int(value,16)
            got = int(dut.data_o.value)
            model[index/4] = got
        
            assert expected == got, f"init failed. exp {hex(expected)}, got {hex(got)}"

        await RisingEdge(dut.clk_i)        

async def test_write(dut, byte_mask) :
    dut.we_i.value = 1
    dut.be_i.value = byte_mask

    for addr in range (numWords) :
        rand_val = random.randint(0, 0xFFFFFFFF)

        old = model.get(addr, 0)
        model[addr] = apply_be(old, rand_val, byte_mask)

        addr *= 4 #convert word address into byte address
        dut.addr_i.value = addr
        dut.data_i.value = (rand_val)
        await ClockCycles(dut.clk_i, 2)

    dut.we_i.value = 0
    await RisingEdge(dut.clk_i)

    #read and compare
    for addr in range (numWords) :
        expected = model.get(addr, 0)
        addr *= 4 #convert word address into byte address
        dut.addr_i.value = addr
        await ClockCycles(dut.clk_i, 2)
        read_value = dut.data_o.value

        assert expected == read_value, f"mem[{addr}] expected {hex(expected)} got {hex(read_value)}"

async def test_not_write(dut, byte_mask) :
        dut.we_i.value = 0

        dut.be_i.value = byte_mask

        #1. write the init values into mem
        for addr in range(numWords):
            addr *= 4 #convert word -> byte address
            dut.addr_i.value = addr
            dut.data_i.value = 0
            await ClockCycles(dut.clk_i, 2)

        await RisingEdge(dut.clk_i)

        #2. read the values from mem and compare   
        for addr in range (numWords):
            expected = model.get(addr, 0)
            addr *= 4 #convert word -> byte address
            dut.addr_i.value = addr
            await ClockCycles(dut.clk_i, 2)
            read_value = dut.data_o.value

            assert expected == read_value, f"mem[{addr}] expected {hex(expected)} got {hex(read_value)}"
    
@cocotb.test()
async def test(dut) :
    clk = Clock(dut.clk_i, 10, "ns")
    clk.start()

    byte_mask = 0b1111
    dut.we_i.value = 0
    dut.data_i.value = 0
    dut.addr_i.value = 0
    
    
    await check_init(dut)

    await test_write(dut, byte_mask)

    byte_mask = 0b1100
    await test_write(dut, byte_mask)
    await test_not_write(dut, byte_mask)

    for byte_mask in range (16):
        await test_write(dut, byte_mask)