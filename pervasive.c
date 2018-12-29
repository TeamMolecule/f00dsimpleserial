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
#include "pervasive.h"

static void pervasive_mask_or(unsigned int addr, unsigned int val)
{
  volatile u32_t tmp;

  tmp = *(volatile u32_t *)addr;
  tmp |= val;
  *(volatile u32_t *)addr = tmp;
  __asm__ volatile ("syncm" ::: "memory");
  tmp = *(volatile u32_t *)addr;
  __asm__ volatile ("syncm" ::: "memory");
}

static void pervasive_mask_and_not(unsigned int addr, unsigned int val)
{
  volatile u32_t tmp;

  tmp = *(volatile u32_t *)addr;
  tmp &= ~val;
  *(volatile u32_t *)addr = tmp;
  __asm__ volatile ("syncm" ::: "memory");
  tmp = *(volatile u32_t *)addr;
  __asm__ volatile ("syncm" ::: "memory");
}

void pervasive_clock_enable_uart(int bus)
{
  pervasive_mask_or(PERVASIVE_GATE_BASE + 0x120 + 4 * bus, 1);
}

void pervasive_reset_exit_uart(int bus)
{
  pervasive_mask_and_not(PERVASIVE_RESET_BASE + 0x120 + 4 * bus, 1);
}

void pervasive_clock_enable_gpio(void)
{
  pervasive_mask_or(PERVASIVE_GATE_BASE + 0x100, 1);
}

void pervasive_reset_exit_gpio(void)
{
  pervasive_mask_and_not(PERVASIVE_RESET_BASE + 0x100, 1);
}
