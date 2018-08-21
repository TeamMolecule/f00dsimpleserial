#include "gpio.h"
#include "vita.h"

#define GPIO_REGS(i)      ((void *)((i) == 0 ? GPIO0_BASE : GPIO1_BASE))

static void gpio_set_port_mode(int bus, int port, int mode)
{
  volatile unsigned int *gpio_regs = GPIO_REGS(bus);

  gpio_regs[0] = (gpio_regs[0] & ~(1 << port)) | (mode << port);

  __asm__ volatile ("syncm" ::: "memory");
}

static void gpio_port_set(int bus, int port)
{
  volatile unsigned int *gpio_regs = GPIO_REGS(bus);

  gpio_regs[2] |= 1 << port;

  gpio_regs[0xD];

  __asm__ volatile ("syncm" ::: "memory");
}

static void gpio_port_clear(int bus, int port)
{
  volatile unsigned int *gpio_regs = GPIO_REGS(bus);

  gpio_regs[3] |= 1 << port;

  gpio_regs[0xD];

  __asm__ volatile ("syncm" ::: "memory");
}
