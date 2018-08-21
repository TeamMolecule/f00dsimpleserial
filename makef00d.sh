mep-elf-gcc -fno-delete-null-pointer-checks -nostdlib -Wl,-T linker.x -fno-optimize-sibling-calls -mc=tiny -Os -std=gnu99 -mel bootstrap.S main.c -o f00d_elf

mep-elf-objcopy -O binary f00d_elf payload.bin

xxd -i payload.bin > payload.h

mep-elf-gcc -nostdlib -Wl,-T loader.x -mc=far -mtf -ml -Os -std=gnu99 -mel  loader.c -lk -o loader_elf
mep-elf-objcopy -O binary loader_elf f00dexec.bin
