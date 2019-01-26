import binascii
import struct
import time
from chipwhisperer.capture.targets.SimpleSerial import SimpleSerial as cwtarget

SCRATCH_ADDR = 0x1F000000
KEYSLOT_OP = 0x101
KEYSLOT_DST = 0x8
TARGET_SLOT = 0x209

def w32(addr, data):
    target.runCommand('w{:08X}{:08X}\\n'.format(addr, data))

def r128(addr):
    target.runCommand('a{:08X}{:08X}\\n'.format(addr, 16))
    return target.readOutput()

def load_slot(slot, data=(0,0,0,0)):
    # first we load the data for keyslot encryption
    w32(SCRATCH_ADDR+0x0, data[0])
    w32(SCRATCH_ADDR+0x4, data[1])
    w32(SCRATCH_ADDR+0x8, data[2])
    w32(SCRATCH_ADDR+0xC, data[3])

    # now we decrypt that using keyslot 0x208 into keyslot 0x8
    # note we cannot decrypt using 0x208 directly
    w32(0xE0050000, SCRATCH_ADDR)
    w32(0xE0050004, KEYSLOT_DST)
    w32(0xE0050008, 0x00000010)
    w32(0xE005000c, 0x10000000 | KEYSLOT_OP)
    w32(0xE0050010, slot)

    # start bigmac
    w32(0xE005001c, 0x00000001)

def zero_buffer(addr, size):
    for i in range(size/4):
        w32(addr+i*4, 0x0)

def do_partial_op(addr, size, op):
    # do bigmac
    w32(0xE0050000, addr) #src
    w32(0xE0050004, addr) #dst
    w32(0xE0050008, size) #size
    w32(0xE005000C, 0x00000080 | op) #op 0x80=supply key
    w32(0xE005001C, 0x00000001) #start op

def get_partial(size):
    # set known key of all zeros
    zero_buffer(0xE0050200, 16)
    # set buffer of zeros
    zero_buffer(SCRATCH_ADDR+0x1000, 16)
    # do forward op
    do_partial_op(SCRATCH_ADDR+0x1000, size, 0x101) # encrypt
    # get partial
    partial = r128(SCRATCH_ADDR+0x1000)
    # do backward op
    do_partial_op(SCRATCH_ADDR+0x1000, size, 0x102) # decrypt
    return partial

def get_final():
    # buf of known plaintext
    zero_buffer(SCRATCH_ADDR+0x1000, 16)
    # setup bigmac
    w32(0xE0050000, SCRATCH_ADDR+0x1000) #src
    w32(0xE0050004, SCRATCH_ADDR+0x1000) #dst
    w32(0xE0050008, 0x00000010) #size
    w32(0xE005000C, 0x00000101) #AES128-ECB encrypt
    w32(0xE0050010, KEYSLOT_DST) #keyslot
    w32(0xE005001C, 0x00000001) #start op
    # get text
    return r128(SCRATCH_ADDR+0x1000)

if __name__ == "__main__" or __name__ == "__builtin__":
    logging.basicConfig(level=logging.WARN)
    try:
        scope = self.scope
        target = self.target
    except NameError:
        scope = cw.scope()
        target = cw.target(scope, cwtarget)
    target.findParam('cmdout').setValue('r$RESPONSE$\\n')
    load_slot(TARGET_SLOT)
    x = get_partial(4)
    print(binascii.hexlify(x))
    x = get_partial(8)
    print(binascii.hexlify(x))
    x = get_partial(12)
    print(binascii.hexlify(x))
    x = get_final()
    print(binascii.hexlify(x))

    
