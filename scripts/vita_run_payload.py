#!/usr/bin/env python2
## 
## vita_run_payload.py -- run brom payloads
##
## Copyright (C) 2018 molecule
##
## This software may be modified and distributed under the terms
## of the MIT license.  See the LICENSE file for details.
## 
from __future__ import print_function, division

import time
import logging
import os
import csv
from enum import IntEnum

import chipwhisperer as cw
import sys
from chipwhisperer.capture.scopes.cwhardware.ChipWhispererExtra import CWExtraSettings
from chipwhisperer.capture.targets.mmccapture_readers._base import MMCPacket
from chipwhisperer.capture.targets.MMCCapture import MMCCapture as cwtarget
from chipwhisperer.common.utils import pluginmanager
from chipwhisperer.capture.targets.simpleserial_readers.cwlite import SimpleSerial_ChipWhispererLite

# Params

CW_SYSCLK_FREQ = 96000000
VITA_CLK_FREQ = 12000000
MIN_OFFSET = 40000 
MAX_OFFSET = 40500
MIN_WIDTH = 1
MAX_WIDTH = 1
VITA_UART0_BAUD = 28985
TIME_RESET_HOLD = 0
TIME_POWER_HOLD = 5
OFFSET_STEP = 1
WIDTH_STEP = 1
GLITCH_FIND_TIMEOUT = 2
WAIT_FOR_UART_TIMEOUT = 3
PAYLOAD_TIMEOUT = 1000
GLOBAL_MAX_TRIES = 100
VERBOSE = 1

class States(IntEnum):
    STARTUP = 0
    IDLE = 1
    PAYLOAD_LOADING = 2
    PAYLOAD_READ = 3
    RESTARTED = 4

# From https://gist.github.com/sbz/1080258
def hexdump(src, offset, length=16):
    FILTER = ''.join([(len(repr(chr(x))) == 3) and chr(x) or '.' for x in range(256)])
    lines = []
    for c in xrange(0, len(src), length):
        chars = src[c:c+length]
        hex = ' '.join(["%02x" % ord(x) for x in chars])
        printable = ''.join(["%s" % ((ord(x) <= 127 and FILTER[ord(x)]) or '.') for x in chars])
        lines.append("%08x  %-*s  %s\n" % (offset + c, length*3, hex, printable))
    return ''.join(lines)


def run_payload(scope, target, timeout=0, verbose=0):
    if not hasattr(target, 'mmc'):
        target = cwtarget()
        target.con(scope)
    # setup parameters needed for glitch the stm32f
    scope.glitch.clk_src = 'clkgen'

    scope.clock.clkgen_freq = VITA_CLK_FREQ
    scope.io.tio1 = "serial_tx"
    scope.io.tio2 = "serial_rx"

    # setup MMC trigger to look for READ_SINGLE_BLOCK of 0x0 response

    mmctrigger = scope.mmcTrigger
    mmctrigger.setMatchCmd(True)
    mmctrigger.setCmdIndex(MMCPacket.Cmd.READ_SINGLE_BLOCK.value)
    mmctrigger.setDirection(2)
    mmctrigger.setDataCompareOp(4)
    mmctrigger.setTriggerData('0x800A')
    mmctrigger.setTriggerNext(True)

    # get MMC output
    mmc = target.mmc

    # get serial console
    ser_cons = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.targets.simpleserial_readers", True, False)
    ser = ser_cons[SimpleSerial_ChipWhispererLite._name]
    ser.con(scope)
    ser.setBaud(VITA_UART0_BAUD)

    # format output table
    headers = ['num packets', 'width', 'offset', 'success']
    #glitch_display = GlitchResultsDisplay(headers)

    # setup trigger
    scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', False)
    scope.advancedSettings.cwEXTRA.setTargetGlitchOut('B', False)
    scope.advancedSettings.cwEXTRA.setTriggerModule(CWExtraSettings.MODULE_MMCTRIGGER)

    # set glitch parameters
    # trigger glitches with external trigger
    scope.glitch.resetDcms()
    scope.glitch.output = 'enable_only'
    scope.glitch.trigger_src = 'ext_continuous'
    scope.io.hs2 = 'clkgen'

    # enable trigger
    scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', True)

    # init
    target.init()

    # power on and hold reset
    if verbose:
        print('Waiting for Vita to power on...')
    scope.io.nrst = 'low'
    scope.io.nrst = 'disabled'
    scope.io.pdid = 'low'
    while mmc.count() == 0:
        pass
    scope.io.pdid = 'disabled'
    scope.io.nrst = 'low'

    if verbose:
        print('Starting glitch...')
    success = False
    tries = 0
    while not success:
        for offset in xrange(MIN_OFFSET, MAX_OFFSET+1, OFFSET_STEP):
            # set offset from trigger
            scope.glitch.ext_offset = offset
            for width in xrange(MIN_WIDTH, MAX_WIDTH+1, WIDTH_STEP):
                if verbose:
                    print('trying offset {}, width {}'.format(offset, width))

                # reset device
                scope.io.nrst = 'low'
                scope.glitch.repeat = width
                #scope.glitch.repeat = 1
                # flush the buffer
                time.sleep(TIME_RESET_HOLD)

                timeout = GLITCH_FIND_TIMEOUT
                # wait for target to finish
                state = States.STARTUP

                last_cnt = 0
                while mmc.count() > 0:
                    pkt = mmc.read()
                    last_cnt = pkt.num
                    if verbose > 1:
                        print(str(pkt))
                count = ser.inWaiting()
                if count > 0:
                    print('WARNING: UART buffer non-empty')
                    ser.read(count)

                scope.io.nrst = 'disabled'
                timestamp = 0
                reads = 0
                while timeout > 0:
                    while mmc.count() > 0:
                        timeout = GLITCH_FIND_TIMEOUT
                        pkt = mmc.read()
                        if pkt.num < last_cnt:
                            timestamp = ((pkt.num + 0x10000 - last_cnt) * 0x100 * 1000.0) / CW_SYSCLK_FREQ
                        else:
                            timestamp = ((pkt.num - last_cnt) * 0x100 * 1000.0) / CW_SYSCLK_FREQ
                        last_cnt = pkt.num
                        if verbose > 1:
                            print('[{:10.5f}ms] {}'.format(timestamp, str(pkt)))
                        if pkt.is_req:
                            if pkt.cmd == MMCPacket.Cmd.READ_SINGLE_BLOCK:
                                reads += 1
                            if state == States.STARTUP:
                                if pkt.cmd == MMCPacket.Cmd.GO_IDLE_STATE:
                                    state = States.IDLE
                            elif state == States.IDLE:
                                if pkt.cmd == MMCPacket.Cmd.READ_SINGLE_BLOCK and pkt.content > 0:
                                    state = States.PAYLOAD_LOADING
                                elif pkt.cmd == MMCPacket.Cmd.GO_IDLE_STATE:
                                    state = States.RESTARTED
                            elif state == States.PAYLOAD_LOADING:
                                if pkt.cmd == MMCPacket.Cmd.SEND_STATUS:
                                    state = States.PAYLOAD_READ
                                elif pkt.cmd == MMCPacket.Cmd.GO_IDLE_STATE:
                                    state = States.RESTARTED
                            elif state == States.PAYLOAD_READ:
                                if pkt.cmd == MMCPacket.Cmd.GO_IDLE_STATE:
                                    state = States.RESTARTED
                        if state == States.RESTARTED:
                            timeout = -1
                            break
                    else:
                        time.sleep(0.1)
                        timeout -= 1

                # for table display purposes
                data = [offset, width, state, reads]
                if verbose:
                    print(data)
                #glitch_display.add_data(data)

                if state == States.PAYLOAD_READ:
                    if verbose:
                        print('Waiting for UART data...')
                    timeout = WAIT_FOR_UART_TIMEOUT
                    count = 0
                    while timeout > 0:
                        count = ser.inWaiting()
                        if count > 0:
                            if verbose:
                                print(ser.read(count))
                            break
                        time.sleep(0.1)
                        timeout -= 1

                    success = (count > 0)

                if success:
                    break
            if success:
                break
        tries += 1
        if timeout > 0 and tries >= timeout:
          return False
    return success

if __name__ == "__main__" or __name__ == "__builtin__":
    logging.basicConfig(level=logging.WARN)
    try:
        scope = self.scope
        target = self.target
    except NameError:
        scope = cw.scope()
        target = cw.target(scope, cwtarget)

    if run_payload(scope, target, GLOBAL_MAX_TRIES, VERBOSE):
        print('Glitch successful.')
    else:
        print('Glitch failed.')

