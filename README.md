# f00dsimpleserial

Implementation of [Simple Serial](https://wiki.newae.com/SimpleSerial) for 
F00D.

## Commands

This is the SimpleSerial protocol with some additional commands for AES256 as 
well as a simple RPC. The only other change is that the trigger is `XD\r\n` 
over UART.

| Command | Example                                                             | Description                                                                                                       | In/Out |
|---------|---------------------------------------------------------------------|-------------------------------------------------------------------------------------------------------------------|--------|
| k       | k2b7e151628aed2a6abf7158809cf4f3c\n                                 | Set AES-128 key                                                                                                   | In     |
| K       | K603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4\n | Set AES-256 key                                                                                                   | In     |
| p       | p6bc1bee22e409f96e93d7e117393172a\n                                 | Send input plain-text, cause encryption                                                                           | In     |
| P       | P6bc1bee22e409f96e93d7e117393172a\n                                 | Send input plain-text using software implementation, cause encryption                                             | In     |
| r       | r3ad77bb40d7a3660a89ecaf32466ef97\n                                 | Result packet for command.                                                                                        | Out    |
| v       | v\n                                                                 | Check protocol version (ACK on v1.1)                                                                              | In     |
| x       | x\n                                                                 | Clears Buffers (resets to 'IDLE' state), does not clear any variables.                                            | In     |
| z       | z00\n                                                               | ACK - Command processing done (with optional status code)                                                         | Out    |
| s       | s0208000810\n                                                       | Set keyslot, dst keyslot, & key length. Two bytes keyslot to use, two bytes dst keyslot (zero for direct). Last byte is 10 for AES128 and 20 for AES256. All big endian. | In     |
| a       | a1F84000000004000\n                                                 | Access memory. First four bytes is address in big endian. Next four bytes is length in big endian.                | In     |
| w       | w3000000000000001\n                                                 | Write 32-bits. First four bytes is address in big endian. Next four bytes is the value in big endian.             | In     |
| R       | R30000000\n                                                         | Read 32-bits. First four bytes is address in big endian. Returns value in big endian.                             | In     |
| j       | j005C0000\n                                                         | Jump to code. Four byte address in big endian. Returns result packet in little endian.                            | In     |
| l       | l00000100\n                                                         | Fast loop. Four byte big endian times. Loops 8*(times+1) times.                                                   | In     |
| L       | L00000100\n                                                         | Slow loop. Four byte big endian times. Loops 4*(times+1) times.                                                   | In     |

## Building

Have the MeP toolchain in your `PATH` and run `make`. `payload.bin` can 
be used with the Petite Mort exception payload. `f00dexec.bin` can be used with 
taif00d.
