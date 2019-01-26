#!/usr/bin/env python2
## 
## setup_cwlite_vita.py -- capture setup for f00d
##
## Copyright (C) 2018 Yifan Lu
##
## This software may be modified and distributed under the terms
## of the MIT license.  See the LICENSE file for details.
## 
from chipwhisperer.capture.scopes.cwhardware.ChipWhispererExtra import CWExtraSettings
import time

try:
    scope = self.scope
    target = self.target
    aux_list = self.aux_list
except NameError:
    raise "Please run this script from CW Capture GUI after a successful glitch!"

VITA_CLK_FREQ = 12000000
VITA_UART0_BAUD = 28985
KEYSLOT = 0
KEYSLOT_DST = 0
KEYLEN = 16

#disable glitch
scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', False)
scope.advancedSettings.cwEXTRA.setTargetGlitchOut('B', False)
    
scope.gain.mode = "low"
scope.gain.gain = 45
scope.adc.samples = 1000
scope.adc.offset = 0
#scope.adc.basic_mode = "rising_edge"
scope.io.hs2 = "disabled"
scope.clock.clkgen_freq = VITA_CLK_FREQ
scope.clock.adc_src = "clkgen_x1"
#scope.trigger.triggers = "tio2"
#scope.decodeIO.set_decodetype(1) # USART
#scope.decodeIO.set_rxbaud(VITA_UART0_BAUD)
#scope.decodeIO.set_triggerpattern(list('XD\r\n'))
scope.edgeTrigger.setPin(True, scope.edgeTrigger.PIN_PDIC)
scope.edgeTrigger.setEdgeStyle(scope.edgeTrigger.EDGE_RISING)
scope.advancedSettings.cwEXTRA.setTriggerModule(CWExtraSettings.MODULE_EDGE)
scope.io.tio1 = "serial_tx"
scope.io.tio2 = "serial_rx"
#scope.advancedSettings.cwEXTRA.setClkgenDivider(2)
#scope.io.hs2 = "clkgen_divided"
scope.io.hs2 = "clkgen"

target.baud = VITA_UART0_BAUD
target.findParam(['proto', 'ver']).setValue('1.1')
target.findParam(['proto', 'timeout']).setValue(100)
target.init()
target.findParam('cmdkey').setValue('k$KEY$\\n')
target.findParam('cmdgo').setValue('p$TEXT$\\n')
target.findParam('cmdout').setValue('r$RESPONSE$\\n')

def setup(scope, target, project):
    if KEYSLOT > 0:
        target.runCommand('s{:04X}{:04X}{:02X}\\n'.format(KEYSLOT, KEYSLOT_DST, KEYLEN))
    elif KEYLEN == 16:
        target.loadEncryptionKey('2b7e151628aed2a6abf7158809cf4f3c')
    else:
        target.runCommand('K603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4\\n')

if 'VITA_BEFORE_CAPTURE_ID' in locals():
  aux_list.remove(VITA_BEFORE_CAPTURE_ID)

VITA_BEFORE_CAPTURE_ID = aux_list.register(setup, "before_capture")

