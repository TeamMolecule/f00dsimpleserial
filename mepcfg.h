#pragma once
// this file is shared between ARM main.c and f00d start.c

enum {
  DATA_ADDR = 0x1F000000,
	DATA_SIZE = 0x4000, // size of buffer for f00d to write data to
	PAYLOAD_ADDR = 0x1F840000, // base addr of payload, make sure it's same as in linker.x
	PAYLOAD_SIZE = 0x20000, // max size of payload
	MSG_OFFSET = PAYLOAD_SIZE - 0x8,
	MSG_ADDR = PAYLOAD_ADDR + MSG_OFFSET, // addr of msg buffer (8 bytes for 1 pointer and 1 size_t)
	MSG_MAGIC = 0xb00bbabe,
};
