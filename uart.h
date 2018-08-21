#pragma once

static int uart_init(int bus);
static int uart_putc(int port, char c);
static int uart_getc(int port);
static void uart_flush_tx(int port);
static void uart_flush_rx(int port);
