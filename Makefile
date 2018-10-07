PREFIX=mep-elf-
CC=$(PREFIX)gcc
CFLAGS=-fno-delete-null-pointer-checks -nostdlib -fno-optimize-sibling-calls -mc=tiny -Os -std=gnu99 -mel
LOADER_CFLAGS=-nostdlib -mc=far -mtf -ml -Os -std=gnu99 -mel
LD=$(PREFIX)gcc
LDFLAGS=-Wl,-T linker.x -nodefaultlibs -nostdlib
OBJCOPY=$(PREFIX)objcopy
OBJCOPYFLAGS=

OBJ=bootstrap.ao main.o gpio.o pervasive.o simpleserial.o uart.o aes.o

all: payload.bin f00dexec.bin

%.o: %.c
	$(CC) -c -o $@ $< $(CFLAGS)

%.ao: %.S
	$(CC) -c -o $@ $< $(CFLAGS)

payload.elf: $(OBJ)
	$(LD) -o $@ $^ $(LDFLAGS)

f00dexec.elf: loader.c loader.x payload.h
	$(CC) -o $@ -Wl,-T loader.x $(LOADER_CFLAGS) loader.c

%.h: %.bin
	xxd -i $< > $@

%.bin: %.elf
	$(OBJCOPY) -O binary $< $@

.PHONY: clean

clean:
	rm -rf *.o *.ao *.elf *.bin payload.h
