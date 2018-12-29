/* simpleserial for f00d
 *
 * Copyright (C) 2018 molecule
 *
 * This software may be modified and distributed under the terms
 * of the MIT license.  See the LICENSE file for details.
 */
#pragma once

int uart_init(int bus);
int uart_putc(int port, char c);
int uart_getc(int port);
void uart_flush_tx(int port);
void uart_flush_rx(int port);
void uart_puts(int port, const char *s);
