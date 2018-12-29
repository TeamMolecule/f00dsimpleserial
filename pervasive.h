/* simpleserial for f00d
 *
 * Copyright (C) 2018 molecule
 *
 * This software may be modified and distributed under the terms
 * of the MIT license.  See the LICENSE file for details.
 */
#pragma once

void pervasive_clock_enable_uart(int bus);
void pervasive_reset_exit_uart(int bus);
void pervasive_clock_enable_gpio(void);
void pervasive_reset_exit_gpio(void);
