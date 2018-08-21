.section .text.start

.global vectors
vectors:
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start
jmp start

.global start
start:
movu $0, 0x5FFF0
mov $sp, $0
lw $gp, (__sdabase)
lw $tp, (__tpbase)
jmp main

.align 2
.global __sdabase
__sdabase:
.word 0x5ea80

.align 2
.global __tpbase
__tpbase:
.word 0x5e7a0
