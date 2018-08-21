/*
 * Copyright (c) 2014 Travis Geiselbrecht
 * Copyright (c) 2015 Yifan Lu
 *
 * Permission is hereby granted, free of charge, to any person obtaining
 * a copy of this software and associated documentation files
 * (the "Software"), to deal in the Software without restriction,
 * including without limitation the rights to use, copy, modify, merge,
 * publish, distribute, sublicense, and/or sell copies of the Software,
 * and to permit persons to whom the Software is furnished to do so,
 * subject to the following conditions:
 *
 * The above copyright notice and this permission notice shall be
 * included in all copies or substantial portions of the Software.
 *
 * THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
 * EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
 * MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.
 * IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY
 * CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION OF CONTRACT,
 * TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION WITH THE
 * SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
 */
#include "libc.h"
#include "vita.h"

#define REG32(addr) ((volatile u32_t *)(addr))
#define UART_REGS(i)            ((void *)(UART_BASE + (i) * 0x10000))
#define UARTCLKGEN_REGS(i)      ((void *)(UART_CLKGEN_BASE + (i) * 4))

static int uart_init(int bus)
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

static int uart_putc(int port, char c)
{
    u32_t base = (u32_t)UART_REGS(port);

    int i = 0;
    while (i++ < 0x1000 && !(*REG32(base + 40) & 0x100));
    *REG32(base + 112) = c;

    return 1;
}

static int uart_getc(int port)
{
    u32_t base = (u32_t)UART_REGS(port);
    int c;

    while (!(*REG32(base + 104) & 0x3F));
    c = *REG32(base + 120);
    *REG32(base + 84) = 0x77F;

    return c;
}

static void uart_flush_tx(int port)
{
    u32_t base = (u32_t)UART_REGS(port);

    int i = 0;
    while (i++ < 0x1000 && !(*REG32(base + 40) & 0x200));
}

static void uart_flush_rx(int port)
{
}
