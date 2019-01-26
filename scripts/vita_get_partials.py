import struct
import time

try:
    target = self.target
except NameError:
    pass

def w32(addr, data):
    target.runCommand('w{:08X}{:08X}\\n'.format(addr, data))

def r32(addr):
    target.runCommand('R{:08X}\\n'.format(addr))
    #ret = target.readOutput()
    #print(ret)

def load_key():
    # first we load the encrypted 0x8 key in memory
    w32(0x1f000000, 0xDEDE414A)
    w32(0x1f000004, 0x4FC0BAFF)
    w32(0x1f000008, 0x002D6052)
    w32(0x1f00000c, 0x66D6DA34)

    # now we decrypt that using keyslot 0x208 into keyslot 0x8
    # note we cannot decrypt using 0x208 directly
    w32(0xE0050000, 0x1f000000)
    w32(0xE0050004, 0x00000020)
    w32(0xE0050008, 0x00000010)
    w32(0xE005000c, 0x10000301)
    w32(0xE0050010, 0x00000344)

    # start bigmac
    w32(0xE005001c, 0x00000001)

def zero_buffer(addr, size):
    for i in range(size/4):
        w32(addr+i*4, 0x0)

def get_partial(size, offset):
    # put key into engine
    load_key()
    # set known key
    zero_buffer(0xE0050200, 16)
    # set buffer of zeros
    zero_buffer(0x1f001000+offset, 16)
    # setup bigmac
    w32(0xE0050000, 0x1f001000+offset) #src
    w32(0xE0050004, 0x1f001000+offset) #dst
    w32(0xE0050008, size) #size
    w32(0xE005000C, 0x00000182) #op 0x80=supply key, 0x100=AES128 bit, 0x2=ecb decrypt
    w32(0xE005001C, 0x00000001) #start op
    # read results
    #r32(0x1f001000)
    #r32(0x1f001004)
    #r32(0x1f001008)
    #r32(0x1f00100c)

get_partial(0xc, 0)
get_partial(0x8, 16)
get_partial(0x4, 32)

def get_final(offset):
    load_key()
    # buf
    zero_buffer(0x1f001000+offset, 16)
    # setup bigmac
    w32(0xE0050000, 0x1f001000+offset) #src
    w32(0xE0050004, 0x1f001000+offset) #dst
    w32(0xE0050008, 0x00000010) #size
    w32(0xE005000C, 0x00000102) #AES128-ECB
    w32(0xE0050010, 0x00000020) #keyslot
    w32(0xE005001C, 0x00000001) #start op

#get_final(48)
