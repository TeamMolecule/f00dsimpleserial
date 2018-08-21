#include "types.h"

void *memcpy(void *dst, const void *src, size_t n) {
  u32_t *dst32 = dst;
  const u32_t *src32 = src;
  size_t i;
  for (i = 0; i < (n/4); i++) {
    dst32[i] = src32[i];
  }
  u8_t *dst8 = dst;
  const u8_t *src8 = src;
  size_t j;
  for (j = i*4; j < n; j++) {
    dst8[j] = src8[j];
  }
  return dst;
}

enum {
  DATA_ADDR = 0x1F000000,
  DATA_SIZE = 0x4000, // size of buffer for f00d to write data to
  PAYLOAD_ADDR = 0x1F840000, // base addr of payload, make sure it's same as in linker.x
  PAYLOAD_SIZE = 0x20000, // max size of payload
  MSG_OFFSET = PAYLOAD_SIZE - 0x8,
  MSG_ADDR = PAYLOAD_ADDR + MSG_OFFSET, // addr of msg buffer (8 bytes for 1 pointer and 1 size_t)
  MSG_MAGIC = 0xb00bbabe,
};

void entry(void) __attribute__ ((section (".text.start")));

enum {
	SECOND_SIZE = 0x4000,
};

#include "payload.h"

void entry(void) {
	void *addr = (void*)0x40000; // same as in linker.x
	void *backup = (void*)0x1F850000;

	memcpy(backup, addr, SECOND_SIZE);
	memcpy(addr, payload_bin, sizeof(payload_bin));

	void (*func)() = addr;
	func();

	memcpy(addr, backup, SECOND_SIZE);
}
