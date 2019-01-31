import binascii
import struct
import time
from chipwhisperer.capture.targets.SimpleSerial import SimpleSerial as cwtarget

SCRATCH_ADDR = 0x1F000000
KEYSLOT_OP = 0x101
KEYSLOT_DST = 0x8
TARGET_SLOT = 0x208

def w32(target, addr, data):
    target.runCommand('w{:08X}{:08X}\\n'.format(addr, data))

def r128(target, addr):
    target.runCommand('a{:08X}{:08X}\\n'.format(addr, 16))
    return target.readOutput()

def load_slot(target, slot, dst, data=(0,0,0,0)):
    # first we load the data for keyslot encryption
    w32(target, SCRATCH_ADDR+0x0, data[0])
    w32(target, SCRATCH_ADDR+0x4, data[1])
    w32(target, SCRATCH_ADDR+0x8, data[2])
    w32(target, SCRATCH_ADDR+0xC, data[3])

    # now we decrypt that using keyslot 0x208 into keyslot 0x8
    # note we cannot decrypt using 0x208 directly
    w32(target, 0xE0050000, SCRATCH_ADDR)
    w32(target, 0xE0050004, dst)
    w32(target, 0xE0050008, 0x00000010)
    w32(target, 0xE005000c, 0x10000000 | KEYSLOT_OP)
    w32(target, 0xE0050010, slot)

    # start bigmac
    w32(target, 0xE005001c, 0x00000001)

def zero_buffer(target, addr, size):
    for i in range(size/4):
        w32(target, addr+i*4, 0x0)

def do_partial_op(target, addr, size, op):
    # do bigmac
    w32(target, 0xE0050000, addr) #src
    w32(target, 0xE0050004, addr) #dst
    w32(target, 0xE0050008, size) #size
    w32(target, 0xE005000C, 0x00000080 | op) #op 0x80=supply key
    w32(target, 0xE005001C, 0x00000001) #start op

def get_partial(target, size, encrypt=True):
    # set known key of all zeros
    zero_buffer(target, 0xE0050200, 16)
    # set buffer of zeros
    zero_buffer(target, SCRATCH_ADDR+0x1000, 16)
    # do forward op
    do_partial_op(target, SCRATCH_ADDR+0x1000, size, 0x101 if encrypt else 0x102) # encrypt
    # get partial
    partial = r128(target, SCRATCH_ADDR+0x1000)
    # do backward op
    do_partial_op(target, SCRATCH_ADDR+0x1000, size, 0x102 if encrypt else 0x101) # decrypt
    return partial

def get_final(target, slot, encrypt=True):
    # buf of known plaintext
    zero_buffer(target, SCRATCH_ADDR+0x1000, 16)
    # setup bigmac
    w32(target, 0xE0050000, SCRATCH_ADDR+0x1000) #src
    w32(target, 0xE0050004, SCRATCH_ADDR+0x1000) #dst
    w32(target, 0xE0050008, 0x00000010) #size
    w32(target, 0xE005000C, 0x101 if encrypt else 0x102) #AES128-ECB
    w32(target, 0xE0050010, slot) #keyslot
    w32(target, 0xE005001C, 0x00000001) #start op
    # get text
    return r128(target, SCRATCH_ADDR+0x1000)

if __name__ == "__main__" or __name__ == "__builtin__":
    logging.basicConfig(level=logging.WARN)
    try:
        scope = self.scope
        target = self.target
    except NameError:
        scope = cw.scope()
        target = cw.target(scope, cwtarget)
    target.findParam('cmdout').setValue('r$RESPONSE$\\n')
    load_slot(target, TARGET_SLOT, KEYSLOT_DST)
    x = get_partial(target, 4)
    print(binascii.hexlify(x))
    x = get_partial(target, 8)
    print(binascii.hexlify(x))
    x = get_partial(target, 12)
    print(binascii.hexlify(x))
    x = get_final(target, KEYSLOT_DST)
    print(binascii.hexlify(x))

    
