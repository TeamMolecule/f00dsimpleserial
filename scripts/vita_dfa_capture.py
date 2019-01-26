from __future__ import print_function, division

import binascii
import time
import logging
import os
import csv
from enum import IntEnum

import chipwhisperer as cw
import sys
from chipwhisperer.capture.scopes.cwhardware.ChipWhispererExtra import CWExtraSettings
from chipwhisperer.capture.targets.mmccapture_readers._base import MMCPacket
from chipwhisperer.capture.targets.MMCCapture import MMCCapture
from chipwhisperer.common.utils import pluginmanager
from chipwhisperer.capture.targets.simpleserial_readers.cwlite import SimpleSerial_ChipWhispererLite
from chipwhisperer.capture.targets.SimpleSerial import SimpleSerial as cwtarget
import vita_run_payload
import vita_get_partials

VITA_UART0_BAUD = 28985
GLITCH_OFFSET = 266
GLITCH_REPEAT = 1
GLITCH_CYCLE_OFFSETS = [10]#[i for i in range(-45,45,5) if i != 0]
GLITCH_CYCLE_WIDTHS = [10]#[i for i in range(-45,45,5) if i != 0]
PAYLOAD_MAX_TRIES = 0 # 0 = max
KNOWN_KEY = '2b7e151628aed2a6abf7158809cf4f3c'
PLAINTEXT = '00000000000000000000000000000000'
BLOCK_LEN = 16
KEYSLOTS = [0x208]
KEYSLOT_DST = 0x8
UNIQUE_SEEN_TARGET = 300
VERBOSE = 1

def do_setup(scope, target):
  # get serial console
  ser_cons = pluginmanager.getPluginsInDictFromPackage("chipwhisperer.capture.targets.simpleserial_readers", True, False)
  ser = ser_cons[SimpleSerial_ChipWhispererLite._name]
  ser.con(scope)
  ser.setBaud(VITA_UART0_BAUD)

  # setup trigger
  scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', False)
  scope.advancedSettings.cwEXTRA.setTargetGlitchOut('B', False)
  scope.edgeTrigger.setPin(True, scope.edgeTrigger.PIN_PDIC)
  scope.edgeTrigger.setEdgeStyle(scope.edgeTrigger.EDGE_RISING)
  scope.advancedSettings.cwEXTRA.setTriggerModule(CWExtraSettings.MODULE_EDGE)

  # set glitch parameters
  # trigger glitches with external trigger
  scope.glitch.resetDcms()
  scope.glitch.trigger_src = 'ext_single'
  scope.glitch.output = 'enable_only'#'glitch_only'
  scope.io.hs2 = 'clkgen'
  scope.glitch.ext_offset = GLITCH_OFFSET
  scope.glitch.repeat = GLITCH_REPEAT

  # setup target
  target.findParam('cmdkey').setValue('k$KEY$\\n')
  target.findParam('cmdgo').setValue('p$TEXT$\\n')
  target.findParam('cmdout').setValue('r$RESPONSE$\\n')
  target.init()

def get_ciphertext(plain):
  target.loadInput(plain)
  scope.arm()
  target.go()
  s = target.readOutput()
  return s

def do_reset_analysis(scope, target):
  do_setup(scope, target)
  # setup key
  target.loadEncryptionKey(KNOWN_KEY)
  # get known plaintext
  exp = get_ciphertext(PLAINTEXT)
  # turn on glitching
  scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', True)
  return exp

def do_reset_slot(scope, target, slot):
  do_setup(scope, target)
  target.findParam('cmdkey').setValue('')
  # setup keyslot
  target.runCommand('s{:04X}{:04X}{:02X}\\n'.format(slot, KEYSLOT_DST, 0x10))
  # get known plaintext
  exp = get_ciphertext(PLAINTEXT)
  # turn on glitching
  scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', True)
  return exp

def do_collection_analysis(scope, target):
  exp = do_reset_analysis(scope, target)
  while exp is None:
    if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
      return
    exp = do_reset_analysis(scope, target)

  seen = set()
  while len(seen) < UNIQUE_SEEN_TARGET:
    for offset in GLITCH_CYCLE_OFFSETS:
      for width in GLITCH_CYCLE_WIDTHS:
        #scope.glitch.offset = offset
        #scope.glitch.width = width
        s = get_ciphertext(PLAINTEXT)
        if s is None:
          if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
            return
          exp = do_reset(scope, target)
        else:
          txt = binascii.hexlify(s)
          if txt in seen:
            print('seen: {}'.format(txt))
          else:
            seen.add(txt)
            print('NEW: {}'.format(txt))

def do_collection_slot(scope, target, slot):
  exp = do_reset_slot(scope, target, slot)
  while exp is None:
    if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
      return
    exp = do_reset_slot(scope, target, slot)

  print('exp: {}'.format(binascii.hexlify(exp)))
  seen = set()

  # get uncorrupted
  p = [None] * 4
  p[0] = binascii.hexlify(vita_get_partials.get_partial(target, 4))
  p[1] = binascii.hexlify(vita_get_partials.get_partial(target, 8))
  p[2] = binascii.hexlify(vita_get_partials.get_partial(target, 12))
  p[3] = binascii.hexlify(vita_get_partials.get_final(target, KEYSLOT_DST))
  print('EXP: {} {} {} {}'.format(p[0], p[1], p[2], p[3]))
  seen.add(p[0])

  while len(seen) < UNIQUE_SEEN_TARGET:
    for offset in GLITCH_CYCLE_OFFSETS:
      for width in GLITCH_CYCLE_WIDTHS:
        #scope.glitch.offset = offset
        #scope.glitch.width = width
        s = get_ciphertext(PLAINTEXT) # ciphertext hidden
        if s is None:
          if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
            return
          do_reset_slot(scope, target, slot)
          continue
        p = [None] * 4
        p[0] = binascii.hexlify(vita_get_partials.get_partial(target, 4))
        if p[0] in seen:
          print('already seen: ' + p[0])
        else:
          seen.add(p[0])
          p[1] = binascii.hexlify(vita_get_partials.get_partial(target, 8))
          p[2] = binascii.hexlify(vita_get_partials.get_partial(target, 12))
          p[3] = binascii.hexlify(vita_get_partials.get_final(target, KEYSLOT_DST))
          print('NEW: {} {} {} {}'.format(p[0], p[1], p[2], p[3]))

try:
  scope = self.scope
  target = self.target
except NameError:
  scope = cw.scope()
  target = cw.target(scope, cwtarget)

do_setup(scope, target)
for slot in KEYSLOTS:
  if slot == 0:
    do_collection_analysis(scope, target)
  else:
    do_collection_slot(scope, target, slot)
print('Done')
