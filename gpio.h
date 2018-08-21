#pragma once

#define GPIO_PORT_MODE_INPUT  0
#define GPIO_PORT_MODE_OUTPUT 1

#define GPIO_PORT_OLED    0
#define GPIO_PORT_SYSCON_OUT  3
#define GPIO_PORT_SYSCON_IN 4
#define GPIO_PORT_GAMECARD_LED  6
#define GPIO_PORT_PS_LED  7
#define GPIO_PORT_HDMI_BRIDGE 15

static void gpio_set_port_mode(int bus, int port, int mode);
static void gpio_port_set(int bus, int port);
static void gpio_port_clear(int bus, int port);
