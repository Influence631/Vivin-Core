import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge, ReadOnly, ReadWrite, ClockCycles
from cocotb.clock import Clock
import random
import logging

log = logging.getLogger("tb.regfile")
log.setLevel(logging.INFO)


ref_regfile = [0] * 32

async def test_write(dut) :
    await RisingEdge(dut.clk_i)
    dut.w_en_i.value = 1

    for i in range(10000) :
        index = random.randint(0,31)
        value = random.randint(0, 0xFFFFFFFF)

        ref_regfile[index] = value

        await RisingEdge(dut.clk_i)
        dut.w_addr_i.value = index
        dut.w_data_i.value = value
        
        await RisingEdge(dut.clk_i)
        
        if (i % 1000 == 0) :
            for r in range(1,32) :
                await RisingEdge(dut.clk_i)
                dut.r1_addr_i.value = r
                await ReadOnly()
                #log.info(f"r{r} = {dut.r1_data_o.value}")    
                assert dut.r1_data_o.value == ref_regfile[r], f"write failed, r{r} expected {ref_regfile[r]}, got {dut.r1_data_o.value}."
        
    await RisingEdge(dut.clk_i)
    dut.w_en_i.value = 0
        

async def test_reset(dut) :
    await FallingEdge(dut.clk_i)
    dut.rst_ni.value = 0
    await ClockCycles(dut.clk_i, 2)
    await FallingEdge(dut.clk_i)
    dut.rst_ni.value = 1 
    for i in range(0, 32) :
        await RisingEdge(dut.clk_i)
        dut.r1_addr_i.value = i
        dut.r2_addr_i.value = i

        await ReadOnly()
        assert dut.r1_data_o.value == 0, f"reset did not work,on port 1, regfile{i} = {dut.r1_data_o.value}"
        assert dut.r2_data_o.value == 0, f"reset did not work on port 2, regfile{i} = {dut.r2_data_o.value}"
        
async def test_zero(dut) :
    await FallingEdge(dut.clk_i)
    dut.w_en_i.value = 1
    dut.rst_ni.value = 1
    dut.w_addr_i.value = 0
    dut.r1_addr_i.value = 0

    for i in range (10):
        dut.w_data_i.value = random.randint(0, 0xFFFFFFFF)
        await RisingEdge(dut.clk_i)

        await ReadOnly()
        assert dut.r1_data_o.value == 0, f"x0 = {dut.r1_data_o.value}, must be 0. "

        await RisingEdge(dut.clk_i)
    
    dut.w_en_i.value = 0

async def test_read_ports(dut) :
    #test identical addresses
    for i in range(0,32) :
        await FallingEdge(dut.clk_i)
        dut.r1_addr_i.value = i
        dut.r2_addr_i.value = i

        await ReadOnly()
        assert dut.r1_data_o.value == dut.r2_data_o.value, f"port 1 != port 2, p1 = {dut.r1_data_o.value} p2 = {dut.r2_data_o.value}"
    
    #test different addresses
    for i in range(0,32) :
        r1 = i
        r2 = 31 - i
        await FallingEdge(dut.clk_i)
        dut.r1_addr_i.value = r1
        dut.r2_addr_i.value = r2

        await ReadOnly()

        if (dut.r1_data_o.value == dut.r2_data_o.value and ref_regfile[r1] != ref_regfile[r2]) :
            assert dut.r1_data_o.value != dut.r2_data_o.value ,(
                f"ports should read different values. " 
                f"p1 = {dut.r1_data_o.value} p2 = {dut.r2_data_o.value}"
                f"expected p1 = {ref_regfile[r1]}, p2 = {ref_regfile[r2]}"
            )
            
    

@cocotb.test()
async def test(dut) :
    
    dut.rst_ni.value = 1
    dut.w_en_i.value = 0
    dut.w_addr_i.value = 0
    dut.w_data_i.value = 0
    dut.r1_addr_i.value = 0
    dut.r2_addr_i.value = 0
    

    clk = Clock(dut.clk_i, 10, "ns")
    clk.start()
    
    await ClockCycles(dut.clk_i, 1)

    await test_write(dut)
        
    await test_read_ports(dut)

    await test_reset(dut)

    await test_zero(dut)


