#include <libk/string.h>
#include "mepcfg.h" // for MSG_ADDR/MSG_MAGIC

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
