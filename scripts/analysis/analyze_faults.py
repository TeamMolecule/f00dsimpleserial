#!/usr/bin/env python3
# aes.py taken from https://github.com/boppreh/aes
from aes import AES
import sys
import binascii
import csv

KEY = binascii.unhexlify('603deb1015ca71be2b73aef0857d77811f352c073b6108d72d9810a30914dff4')
TXT = binascii.unhexlify('00000000000000000000000000000000')
EXP = binascii.unhexlify('E568F68194CF76D6174D4CC04310A854')
ENCRYPT = False
#KEY = binascii.unhexlify('2b7e151628aed2a6abf7158809cf4f3c')
#EXP = binascii.unhexlify('7df76b0c1ab899b33e42f047b91b546f')
THRESHOLD = 32

def bits(x):
    n = 0
    for y in x:
        while y != 0:
            if y & 1:
                n += 1
            y = y >> 1
    return n

def find_fault_encrypt(log):
    lastsum = 128
    lastr = 10 if len(KEY) == 16 else 14
    lasts = 3
    for r in range(lastr, -1, -1):
        for s in range(3, -1, -1):
            if log[r][s] is None:
                continue
            diffsum = bits(log[r][s])
            if diffsum <= lastsum:
                lastsum = diffsum
                lastr = r
                lasts = s
    return (lastr, lasts)

def find_fault_decrypt(log):
    lastsum = 128
    lastr = 0
    lasts = 3
    for r in range(0, 11 if len(KEY) == 16 else 15):
        for s in range(0, 4):
            if log[r][s] is None:
                continue
            diffsum = bits(log[r][s])
            if diffsum <= lastsum:
                lastsum = diffsum
                lastr = r
                lasts = s
    return (lastr, lasts)

def parse(ct):
    ctb = binascii.unhexlify(ct)
    aes = AES(KEY)
    if ENCRYPT:
      log = aes.decrypt_diff(EXP, ctb)
      (r, s) = find_fault_encrypt(log)
    else:
      log = aes.encrypt_diff(TXT, ctb)
      (r, s) = find_fault_decrypt(log)
    diffsum = bits(log[r][s])
    if diffsum < THRESHOLD:
        print('{}, {}, bits={}, round={}, before={}'.format(ct, binascii.hexlify(log[r][s]), diffsum, r, AES.Step(s).name))
    return r, s, diffsum

with open(sys.argv[1]) as fp:
    line = fp.readline()
    while line:
        ct = line[0:32]
        r,s,d = parse(ct)
        line = fp.readline()
