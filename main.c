#include "libc.h"

#define SS_VER SS_VER_1_1

#include "uart.c"
#include "pervasive.c"
#include "gpio.c"
#include "simpleserial.c"

static volatile u32_t * const BIGMAC = (void *)0xE0050000;
static volatile void * const BIGMAC_KEY = (void *)0xE0050200;
static u32_t g_keyslot;
static u32_t g_len;
static u32_t g_key[8];
static u32_t g_offset;

void *memcpy(void *dst, const void *src, size_t n) {
  u32_t *dst32 = dst;
  const u32_t *src32 = src;
  size_t i;
  for (i = 0; i < (n/4); i++) {
    dst32[i] = src32[i];
  }
  u8_t *dst8 = dst;
  const u8_t *src8 = src;
  size_t j;
  for (j = i*4; j < n; j++) {
    dst8[j] = src8[j];
  }
  return dst;
}

static u8_t get_key128(u8_t* k)
{
  memcpy(g_key, k, 16);
  g_keyslot = 0;
  g_len = 16;
  return 0x00;
}

static u8_t get_key256(u8_t* k)
{
  memcpy(g_key, k, 32);
  g_keyslot = 0;
  g_len = 32;
  return 0x00;
}

static u8_t get_pt(u8_t* pt)
{
  /**********************************
  * Start user-specific code here. */

  // setup params

  u32_t param = 0x1;
  if (g_len == 16) {
    param |= 0x100;
  } else {
    param |= 0x300;
  }
  if (g_keyslot == 0) {
    param |= 0x80;
    memcpy((void *)BIGMAC_KEY, g_key, 32);
  }

  BIGMAC[0] = (u32_t)pt;
  BIGMAC[1] = (u32_t)pt;
  BIGMAC[2] = 16;
  BIGMAC[3] = param;
  BIGMAC[4] = g_keyslot;

  uart_putc(DEBUG_PORT, 'X');
  uart_putc(DEBUG_PORT, 'D');
  uart_putc(DEBUG_PORT, '\r');
  uart_putc(DEBUG_PORT, '\n');

  for (volatile register int i = 0; i < g_offset; i++);

  // start processing
  BIGMAC[7] = 1;

  while (BIGMAC[9] & 1) {}
  
  //trigger_low();
  /* End user-specific code here. *
  ********************************/
  simpleserial_put('r', 16, pt);
  return 0x00;
}

static u8_t get_keyslot(u8_t* x)
{
  g_keyslot = (x[0] << 8) | x[1];
  g_len = x[2];
  return 0x00;
}

static u8_t reset(u8_t* x)
{
  g_keyslot = 0;
  g_len = 16;
  for (int i = 0; i < 8; i++) {
    g_key[i] = 0;
  }
  g_offset = 0;
  return 0x00;
}

static u8_t access_mem(u8_t* x)
{
  u32_t addr = (x[0] << 24) | (x[1] << 16) | (x[2] << 8) | x[3];
  u32_t len = (x[4] << 24) | (x[5] << 16) | (x[6] << 8) | x[7];
  simpleserial_put('r', len, (void *)addr);
  return 0x00;
}

static u8_t write32(u8_t* x)
{
  u32_t addr = (x[0] << 24) | (x[1] << 16) | (x[2] << 8) | x[3];
  u32_t word = (x[4] << 24) | (x[5] << 16) | (x[6] << 8) | x[7];
  *(u32_t *)addr = word;
  return 0x00;
}

static u8_t jump(u8_t* x)
{
  u32_t addr = (x[0] << 24) | (x[1] << 16) | (x[2] << 8) | x[3];
  u32_t res = ((u32_t (*)(void))addr)();
  simpleserial_put('r', 4, (u8_t *)&res);
  return 0x00;
}

static u8_t set_offset(u8_t* x)
{
  g_offset = (x[0] << 24) | (x[1] << 16) | (x[2] << 8) | x[3];
  return 0x00;
}

void main(void) {
  pervasive_clock_enable_gpio();
  pervasive_reset_exit_gpio();
  pervasive_clock_enable_uart(DEBUG_PORT);
  pervasive_reset_exit_uart(DEBUG_PORT);

  uart_init(DEBUG_PORT);

  gpio_set_port_mode(0, GPIO_PORT_GAMECARD_LED, GPIO_PORT_MODE_OUTPUT);
  gpio_port_set(0, GPIO_PORT_GAMECARD_LED);

  reset((void *)0);
  simpleserial_init();    
  simpleserial_addcmd('k', 16, get_key128);
  simpleserial_addcmd('K', 32, get_key256);
  simpleserial_addcmd('s', 3, get_keyslot);
  simpleserial_addcmd('p', 16, get_pt);
  simpleserial_addcmd('x', 0, reset);
  simpleserial_addcmd('a', 8, access_mem);
  simpleserial_addcmd('w', 8, write32);
  simpleserial_addcmd('j', 4, jump);
  simpleserial_addcmd('o', 4, set_offset);
  while (1) {
    simpleserial_get();
  }
}
