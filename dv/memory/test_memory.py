import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
import random
import logging

log = logging.getLogger("tb.memory")
log.setLevel(logging.INFO)

init_data = []

numWords = 128
byte_mask = 12

async def test_write(dut) :
    dut.w_en_i.value = 1

    dut.byte_enable_i.value = byte_mask

    #1. write the init values into mem
       
    for addr in range (numWords) :
        rand_val = random.randint(0, 0xFFFFFFFF)

        init_data.append(rand_val)

        dut.addr_i.value = addr
        dut.data_i.value = (rand_val)
        await ClockCycles(dut.clk_i, 2)

    dut.w_en_i.value = 0
    await RisingEdge(dut.clk_i)

    #2. read the init values from the mem and compare   
    for i in range (numWords) :
        value = init_data[i]
        dut.addr_i.value = i
        await ClockCycles(dut.clk_i, 2)
        read_value = dut.data_o.value

        expected_value = 0 
        for i in range(4) :
            if ((byte_mask >> i) & 1) :
                expected_value |= value & (0xFF << i * 8)
        assert expected_value == read_value, f"mem[{addr}] expected {hex(expected_value)} got {hex(read_value)}"



async def test_not_write(dut) :
        dut.w_en_i.value = 0

        dut.byte_enable_i.value = byte_mask

        #1. write the init values into mem
        for addr in range(numWords):
            dut.addr_i.value = addr
            dut.data_i.value = 0
            await ClockCycles(dut.clk_i, 2)

        await RisingEdge(dut.clk_i)

        #2. read the values from the mem and compare   
        for addr in range (numWords):
            value = init_data[addr]
            dut.addr_i.value = addr
            await ClockCycles(dut.clk_i, 2)
            read_value = dut.data_o.value

            log.warning(hex(read_value))
            
            expected_value = 0 
            for i in range(4) :
                if ((byte_mask >> i) & 1) :
                    expected_value |= value & (0xFF << i * 8)
            assert expected_value == read_value, f"mem[{addr}] expected {hex(expected_value)} got {hex(read_value)}"

    
@cocotb.test()
async def test(dut) :
    clk = Clock(dut.clk_i, 10, "ns")
    clk.start()

    dut.w_en_i.value = 0
    dut.data_i.value = 0
    dut.addr_i.value = 0

    await test_write(dut)

    await test_not_write(dut)

    
