#!/usr/bin/env python3
from JeanGrey.phoenixAES import phoenixAES
import binascii
import sys

ENCRYPT = False

def main(keylen, last_round_file, second_round_file=None):
    candidates = []
    with open(last_round_file, "r") as fp:
        for line in fp:
            candidates.append(bytearray.fromhex(line.strip()))
    last_round = None
    for i in range(1, len(candidates)):
        for j in range(i+1, len(candidates)):
            r9faults = phoenixAES.convert_r8faults_bytes((candidates[i], candidates[j]), candidates[0], encrypt=ENCRYPT)
            res = phoenixAES.crack_bytes(r9faults, candidates[0], encrypt=ENCRYPT, verbose=0)
            if res is not None:
                last_round = bytearray.fromhex(res)
                break
        if last_round is not None:
            break
    if keylen == 128 or last_round is None:
        return last_round
    # get second to last round
    if second_round_file is not None:
        candidates = []
        with open(second_round_file, "r") as fp:
            for line in fp:
                candidates.append(bytearray.fromhex(line.strip()))
    candidates = [phoenixAES.rewind(c, [last_round], encrypt=ENCRYPT, mimiclastround=True) for c in candidates]
    second_round = None
    for i in range(1, len(candidates)):
        for j in range(i+1, len(candidates)):
            r9faults = phoenixAES.convert_r8faults_bytes((candidates[i], candidates[j]), candidates[0], encrypt=ENCRYPT)
            res = phoenixAES.crack_bytes(r9faults, candidates[0], encrypt=ENCRYPT, verbose=0)
            if res is not None:
                second_round = bytearray.fromhex(res)
                break
        if second_round is not None:
            break
    if second_round is None:
        return last_round
    else:
        return last_round + second_round

if __name__ == "__main__":
    if len(sys.argv) < 3:
        print('usage: python3 crack_all.py 256|128 round_n_minus_3.txt [round_n_minus_4.txt]')
        sys.exit()
    r = main(int(sys.argv[1]), sys.argv[2], sys.argv[3] if len(sys.argv) > 3 else None)
    if r is not None:
        print(''.join(['{:02X}'.format(c) for c in r]))
    else:
        print('unknown')


