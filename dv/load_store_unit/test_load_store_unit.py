import cocotb
from cocotb.triggers import Timer
import random
import logging
from enum import IntEnum
from dataclasses import dataclass, field

log = logging.getLogger("tb.load_store_unit")
log.setLevel(logging.INFO)
timer = Timer(1, "ns")

NTESTS = 1000

class SIZE(IntEnum) :
    BYTE = 0
    HALF = 1
    WORD = 2

@dataclass(kw_only=True)
class STORE:
    size : int = 0
    signed : int = 0
    value : int = 0
    offset : int = 0
    misaligned : int = field(init=False, default=0)

    @staticmethod
    def create_random()  :
        return STORE(
            size = random.choice([SIZE.BYTE, SIZE.HALF, SIZE.WORD]),
            signed = random.choice([0,1]),
            value = random.randint(0, 2*32 - 1),
            offset = random.randint(0, 3)
        ) 

    def __post_init__(self) : 
        self.misaligned = 0 if self.offset % self.get_access_size() == 0 else 1

    def get_access_size(self) :
        if (self.size == SIZE.BYTE) :
            return 1
        elif (self.size == SIZE.HALF) :
            return 2
        return 4

    def get_be(self) :
        match (self.size) :
            case SIZE.BYTE :
                match (self.offset) :
                    case 0 : return 0b0001
                    case 1 : return 0b0010
                    case 2 : return 0b0100
                    case 3 : return 0b1000
            case SIZE.HALF :
                match (self.offset) :
                    case 0 : return 0b0011
                    case 2 : return 0b1100
            case SIZE.WORD :
                match (self.offset) :
                    case 0 : return 0b1111
        return 0b0000 #default 

@dataclass(kw_only=True)
class LOAD:
    size : int = 0
    signed : int = 0
    mem_rdata : int = 0
    offset : int = 0
    final_value : int = field(init=False, default=0)
    misaligned : int = field(init=False, default=0)

    @staticmethod
    def create_random()  :
        return LOAD(
            size = random.choice([SIZE.BYTE, SIZE.HALF, SIZE.WORD]),
            signed = random.choice([0,1]),
            mem_rdata = random.randint(0, 2*32 - 1),
            offset = random.randint(0, 3)
        ) 

    def get_final_load_value(self):
      data = self.mem_rdata.to_bytes(4, 'little')
      n = self.get_access_size()
      chunk = data[self.offset : self.offset + n]
      return int.from_bytes(chunk, 'little', signed=self.signed) & 0xFFFFFFFF

    def __post_init__(self) : 
        self.misaligned = 0 if self.offset % self.get_access_size() == 0 else 1
        self.final_value = self.get_final_load_value()

    def get_access_size(self) :
        if (self.size == SIZE.BYTE) :
            return 1
        elif (self.size == SIZE.HALF) :
            return 2
        return 4

async def test_load(dut):
    for i in range (0, NTESTS) :
        load = LOAD.create_random()

        dut.mem_rdata_i.value = load.mem_rdata
        dut.is_signed_i.value = load.signed
        dut.size_i.value = load.size
        dut.addr_offset_i.value = load.offset

        expected_value = load.final_value

        await timer

        assert dut.misaligned_o.value == load.misaligned, f"{load} : \n misaligned exp {load.misaligned}, got {dut.misaligned_o}"
        if not (load.misaligned) :  
            assert dut.load_rdata_o.value == expected_value,f"{load} : \n expected load_rdata_o {bin(expected_value)}, got {dut.load_rdata_o.value}"


async def test_write(dut):
    for i in range (0, NTESTS) :
        store = STORE.create_random()

        dut.store_wdata_i.value = store.value
        dut.is_signed_i.value = store.signed
        dut.size_i.value = store.size
        dut.addr_offset_i.value = store.offset 

        await timer

        expected_value = store.value

        if (store.size == SIZE.BYTE or store.size == SIZE.HALF) :
            expected_value = store.value <<  store.offset * 8

        await timer

        assert dut.misaligned_o.value == store.misaligned, f"{store} : \n misaligned exp {store.misaligned}, got {dut.misaligned_o}"
        assert dut.mem_be_o.value == store.get_be(), f"{store} : \n mem_be_o exp {bin(store.get_be())}, got {bin(dut.mem_be_o.value)}" 
        if not (store.misaligned) :  
            assert dut.mem_wdata_o.value == expected_value,f"{store} : \n expected mem_wdata_o {bin(expected_value)}, got {dut.mem_wdata_o.value}"


@cocotb.test()
async def test_random(dut) :
    dut.size_i.value = SIZE.BYTE
    dut.is_signed_i.value = 0
    dut.addr_offset_i.value = 0
    dut.mem_rdata_i.value = 0
    dut.store_wdata_i.value = 0

    await test_write(dut)
    await test_load(dut)