/* simpleserial for f00d
 *
 * Copyright (C) 2018 molecule
 *
 * This software may be modified and distributed under the terms
 * of the MIT license.  See the LICENSE file for details.
 */
#include "config.h"
#include "types.h"
#include "vita.h"
#include "uart.h"

#define REG32(addr) ((volatile u32_t *)(addr))
#define UART_REGS(i)            ((void *)(UART_BASE + (i) * 0x10000))
#define UARTCLKGEN_REGS(i)      ((void *)(UART_CLKGEN_BASE + (i) * 4))

int uart_init(int bus)
{
    volatile unsigned int *uart_regs = UART_REGS(bus);
    volatile unsigned int *uartclkgen_regs = UARTCLKGEN_REGS(bus);

    uart_regs[1] = 0; // disable device

    *uartclkgen_regs = 0x1001A; // Baudrate = 115200

    uart_regs[8] = 3;
    uart_regs[4] = 1;
    uart_regs[0xC] = 0;
    uart_regs[0x18] = 0x303;
    uart_regs[0x10] = 0;
    uart_regs[0x14] = 0;
    uart_regs[0x19] = 0x10001;

    uart_regs[1] = 1; // enable device

    int i = 0;
    while (i++ < 0x1000 && !(uart_regs[0xA] & 0x200));

    return 0;
}

int uart_putc(int port, char c)
{
    u32_t base = (u32_t)UART_REGS(port);

    int i = 0;
    while (i++ < 0x1000 && !(*REG32(base + 40) & 0x100));
    *REG32(base + 112) = c;

    return 1;
}

int uart_getc(int port)
{
    u32_t base = (u32_t)UART_REGS(port);
    int c;

    while (!(*REG32(base + 104) & 0x3F));
    c = *REG32(base + 120);
    *REG32(base + 84) = 0x77F;

    return c;
}

void uart_flush_tx(int port)
{
    u32_t base = (u32_t)UART_REGS(port);

    int i = 0;
    while (i++ < 0x1000 && !(*REG32(base + 40) & 0x200));
}

void uart_flush_rx(int port)
{
}

void uart_puts(int port, const char *s) {
    while (*s) {
        uart_putc(port, *s);
        if (*s == '\n') {
            uart_flush_tx(port);
        }
        s++;
    }
}
