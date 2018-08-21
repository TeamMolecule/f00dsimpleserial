/*
 * Copyright (c) 2012-2014 Travis Geiselbrecht
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
#pragma once

#define SDRAM_BASE          (0x40000000)
#define DEVICE_BASE         (0xE0000000)
#define DEVICE_SIZE         (0x08400000)
#define DEVICE_2_BASE       (0xEC000000)
#define DEVICE_2_SIZE       (0x02700000)

#define CPUPRIV_BASE        (0x1A000000)
#define CPUPRIV_SIZE        (0x00003000)

#define SCRATCH_BASE        (0x1F000000)
#define SCRATCH_SIZE        (0x00008000)

#define DISPLAY_BASE        (0x1C000000)
#define DISPLAY_SIZE        (0x00200000)
#define DISPLAY_WIDTH       (960)
#define DISPLAY_HEIGHT      (480)

/* UART */
#define UART_BASE (DEVICE_BASE + 0x2030000)
#define UART0_BASE (UART_BASE + 0x00000)
#define UART1_BASE (UART_BASE + 0x10000)
#define UART2_BASE (UART_BASE + 0x20000)
#define UART3_BASE (UART_BASE + 0x30000)
#define UART4_BASE (UART_BASE + 0x40000)
#define UART5_BASE (UART_BASE + 0x50000)
#define UART6_BASE (UART_BASE + 0x60000)

#define UART_CLKGEN_BASE (DEVICE_BASE + 0x3105000)

#define PERVASIVE_RESET_BASE (DEVICE_BASE + 0x3101000)
#define PERVASIVE_RESET_SPI (PERVASIVE_RESET_BASE + 0x104)
#define PERVASIVE_RESET_UART (PERVASIVE_RESET_BASE + 0x120)
#define PERVASIVE_GATE_BASE (DEVICE_BASE + 0x3102000)
#define PERVASIVE_GATE_UART (PERVASIVE_GATE_BASE + 0x120)

#define IFTU0_BASE (DEVICE_BASE + 0x5020000)
#define IFTU1_BASE (DEVICE_BASE + 0x5030000)
#define IFTU2_BASE (DEVICE_BASE + 0x5040000)

#define GPIO0_BASE (DEVICE_BASE + 0x20A0000)
#define GPIO1_BASE (DEVICE_BASE + 0x0100000)
#define SPI2_BASE (DEVICE_BASE + 0x0A20000)

/* interrupts */
#define IFTU0A_INT (204)
#define DSI0_INT (213)
#define UART1_INT (225)

#define MAX_INT 256

