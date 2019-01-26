import struct
import time

try:
    target = self.target
except NameError:
    pass

PAYLOAD = '~/f00dsimpleserial/f00dexec.bin'
ADDR = 0x1F840000

with open(PAYLOAD, 'rb') as fp:
    addr = ADDR
    while True:
        buf = fp.read(4)
        if not buf:
            break
        dat = struct.unpack('<I', buf)[0]
        target.runCommand('w{:08X}{:08X}\\n'.format(addr, dat))
        addr += 4
    target.runCommand('j{:08X}\\n'.format(ADDR))
