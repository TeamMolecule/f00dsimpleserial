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

VITA_UART0_BAUD = 28985
GLITCH_OFFSET = 266
GLITCH_REPEAT = 1
GLITCH_CYCLE_OFFSETS = [10]#[i for i in range(-45,45,5) if i != 0]
GLITCH_CYCLE_WIDTHS = [10]#[i for i in range(-45,45,5) if i != 0]
MAX_TRIES = 50000
PAYLOAD_MAX_TRIES = 0 # 0 = max
KNOWN_KEY = 'ffffffffffffffffffffffffffffffff'
PLAINTEXT = 'ffffffffffffffffffffffffffffffff'
BLOCK_LEN = 16
VERBOSE = 1
_AesFaultMaps= [
# AES decryption
 [[True, False, False, False, False, True, False, False, False, False, True, False, False, False, False, True],
  [False, True, False, False, False, False, True, False, False, False, False, True, True, False, False, False],
  [False, False, True, False, False, False, False, True, True, False, False, False, False, True, False, False],
  [False, False, False, True, True, False, False, False, False, True, False, False, False, False, True, False]],
# AES encryption
 [[True, False, False, False, False, False, False, True, False, False, True, False, False, True, False, False],
  [False, True, False, False, True, False, False, False, False, False, False, True, False, False, True, False],
  [False, False, True, False, False, True, False, False, True, False, False, False, False, False, False, True],
  [False, False, False, True, False, False, True, False, False, True, False, False, True, False, False, False]]
]

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

def xor(b1, b2):
  """
  XOR two bytearrays

  :param b1: first bytearray
  :param b2: second bytearray
  :returns: new bytearray
  """
  result = bytearray()
  for b1, b2 in zip(b1, b2):
      result.append(b1 ^ b2)
  return result

def is_good(ref, pt):
  diff=xor(ref, pt)
  diffmap=[x!=0 for x in diff]
  diffsum=sum(diffmap)
  if VERBOSE > 0:
    print('{}, diffsum={}, good={}'.format(binascii.hexlify(pt), diffsum, diffmap in _AesFaultMaps[True]))
  if diffsum==4 and diffmap in _AesFaultMaps[True]:
    return True
  else:
    return False

def get_ciphertext(plain):
  target.loadInput(plain)
  scope.arm()
  target.go()
  s = target.readOutput()
  return s

def do_reset(scope, target):
  do_setup(scope, target)
  # setup key
  target.loadEncryptionKey(KNOWN_KEY)
  # get known plaintext
  exp = get_ciphertext(PLAINTEXT)
  # turn on glitching
  scope.advancedSettings.cwEXTRA.setTargetGlitchOut('A', True)
  return exp

def do_collection(scope, target):
  exp = do_reset(scope, target)

  for _ in range(MAX_TRIES):
    for offset in GLITCH_CYCLE_OFFSETS:
      for width in GLITCH_CYCLE_WIDTHS:
        scope.glitch.offset = offset
        scope.glitch.width = width
        s = get_ciphertext(PLAINTEXT)
        if s is None:
          if not vita_run_payload.run_payload(scope, target, PAYLOAD_MAX_TRIES, VERBOSE):
            return
          exp = do_reset(scope, target)
        elif is_good(exp, s):
          if VERBOSE:
            print('good=True, offset: {}, width: {}'.format(offset, width))
          print(binascii.hexlify(s))

try:
  scope = self.scope
  target = self.target
except NameError:
  scope = cw.scope()
  target = cw.target(scope, cwtarget)

do_setup(scope, target)
do_collection(scope, target)
print('Done')
