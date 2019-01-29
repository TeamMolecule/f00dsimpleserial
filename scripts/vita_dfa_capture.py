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
USE_4X_CLOCK = True
GLITCH_OFFSETS = range(265*4, 272*4)
GLITCH_REPEAT = 1*4
PAYLOAD_MAX_TRIES = 0 # 0 = max
#KNOWN_KEY = bytearray(binascii.unhexlify('2b7e151628aed2a6abf7158809cf4f3c'))
KNOWN_KEY = bytearray(binascii.unhexlify('603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4'))
KEY_LEN = len(KNOWN_KEY)
PLAINTEXT = '00000000000000000000000000000000'
#PLAINTEXT = 'E568F68194CF76D6174D4CC04310A854'
ENCRYPT = False
KEYSLOTS = [[0x216,0]]
UNIQUE_SEEN_TARGET = 5000
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
  scope.glitch.repeat = GLITCH_REPEAT
  
  # set new clock
  if USE_4X_CLOCK:
    scope.io.hs2 = "disabled"
    scope.clock.clkgen_freq *= 4
    scope.advancedSettings.cwEXTRA.setClkgenDivider(2)
    scope.io.hs2 = 'clkgen_divided'
  else:
    scope.io.hs2 = 'clkgen'

  # setup target
  if KEY_LEN == 32:
    target.findParam('cmdkey').setValue('K$KEY$\\n')
  else:
    target.findParam('cmdkey').setValue('k$KEY$\\n')
  target.findParam('cmdgo').setValue('p$TEXT$\\n')
  target.findParam('cmdout').setValue('r$RESPONSE$\\n')
  target.key_len = KEY_LEN
  target.init()

  do_set_encrypt(target, ENCRYPT)

def get_ciphertext(plain):
  target.loadInput(plain)
  scope.arm()
  target.go()
  s = target.readOutput()
  return s

def do_set_encrypt(target, encrypt):
  # patch the code for decrypt
  if not encrypt:
    target.runCommand('w00040340c3ee0302\\n')
    target.runCommand('w00040338e2310102\\n')

def do_reset_analysis(scope, target):
  do_setup(scope, target)
  # setup key
  target.loadEncryptionKey(KNOWN_KEY)
  # get known plaintext
  exp = get_ciphertext(PLAINTEXT)
  # turn on glitching
  scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', True)
  return exp

def do_reset_slot(scope, target, slot, dst_slot):
  do_setup(scope, target)
  target.findParam('cmdkey').setValue('')
  # setup keyslot
  target.runCommand('s{:04X}{:04X}{:02X}\\n'.format(slot, dst_slot, KEY_LEN))
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
  exp_txt = binascii.hexlify(exp)
  print('EXP: @0000 {}'.format(exp_txt))

  seen = set([exp_txt])
  while len(seen) < UNIQUE_SEEN_TARGET:
    for offset in GLITCH_OFFSETS:
      scope.glitch.ext_offset = offset
      s = get_ciphertext(PLAINTEXT)
      if s is None:
        if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
          return
        exp = do_reset_analysis(scope, target)
      else:
        txt = binascii.hexlify(s)
        if txt in seen:
          print('seen: {}'.format(txt))
        else:
          seen.add(txt)
          print('NEW: @{:04} {}'.format(offset, txt))

def get_partials(target, slot, first=None):
  p = [None] * 4
  if first is None:
    p[0] = binascii.hexlify(vita_get_partials.get_partial(target, 4))
  else:
    p[0] = first
  p[1] = binascii.hexlify(vita_get_partials.get_partial(target, 8))
  p[2] = binascii.hexlify(vita_get_partials.get_partial(target, 12))
  p[3] = binascii.hexlify(vita_get_partials.get_final(target, slot))
  return p

def do_collection_slot(scope, target, slot, dst_slot):
  exp = do_reset_slot(scope, target, slot, dst_slot)
  while exp is None:
    if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
      return
    exp = do_reset_slot(scope, target, slot, dst_slot)

  exp_txt = binascii.hexlify(exp)
  print('exp: {}'.format(exp_txt))
  seen = set()
  needs_partials = (dst_slot != 0)

  # get uncorrupted
  if needs_partials:
    p = get_partials(target, dst_slot)
    print('EXP: @{:04} PARTIAL:{:03X} {} {} {} {}'.format(0, slot, p[0], p[1], p[2], p[3]))
    seen.add(p[0])
  else:
    seen.add(exp_txt)
    print('EXP: @{:04} SLOT:{:03X} {}'.format(0, slot, exp_txt))

  while len(seen) < UNIQUE_SEEN_TARGET:
    for offset in GLITCH_OFFSETS:
      scope.glitch.ext_offset = offset
      s = get_ciphertext(PLAINTEXT) # ciphertext hidden
      if s is None:
        if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
          return
        do_reset_slot(scope, target, slot, dst_slot)
        continue
      if needs_partials:
        tst = binascii.hexlify(vita_get_partials.get_partial(target, 4))
        if tst in seen:
          print('already seen: ' + p[0])
        else:
          seen.add(tst)
          p = get_partials(target, dst_slot, first=tst)
          print('NEW: @{:04} PARTIAL:{:03X} {} {} {} {}'.format(offset, slot, p[0], p[1], p[2], p[3]))
      else:
        txt = binascii.hexlify(s)
        if txt in seen:
          print('seen: {}'.format(txt))
        else:
          seen.add(txt)
          print('NEW: @{:04} SLOT:{:03X} {}'.format(offset, slot, txt))

try:
  scope = self.scope
  target = self.target
except NameError:
  scope = cw.scope()
  target = cw.target(scope, cwtarget)

do_setup(scope, target)
for slot,dst_slot in KEYSLOTS:
  if slot == 0:
    do_collection_analysis(scope, target)
  else:
    do_collection_slot(scope, target, slot, dst_slot)
print('Done')
