import cocotb
from cocotb.triggers import Timer, RisingEdge, FallingEdge
from cocotb.clock import Clock

half = Timer(1, "ns")

@cocotb.test()
async def test(dut) :
    clock = Clock(dut.clk_i, 10, "ns")
    clock.start()

    await RisingEdge(dut.clk_i)

    await half
    dut.rst_ni.value = 0

    await RisingEdge(dut.clk_i)
    dut.rst_ni.value = 1
    dut.w_en_i.value = 1
    dut.w_data_i.value = 5
    dut.w_addr_i.value = 6
    dut.r1_addr_i.value = 6
    await RisingEdge(dut.clk_i)
    await RisingEdge(dut.clk_i)

    dut.w_en_i.value = 0
    cocotb.log.info(f"the x6 is {dut.r1_data_o.value}")