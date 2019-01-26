ChipWhisperer Scripts
=====================
You must have payload.bin flashed to your eMMC and the MBR patched to point to 
it.

All the scripts (except `setup_cwlite_vita.py`) can be run from the command 
line or the CW GUI. Open the files to modify their params.

## setup_cwlite_vita.py
Run after `vita_run_payload.py` to setup target params.

## vita_dfa_capture.py
Does DFA attack on keyslots.

## vita_get_partials.py
Extracts partials

## vita_reload_payload.py
Loads `f00dexec.bin` and jumps to it

## vita_run_payload.py
Does the Petite Mort glitch attack to execute the payload.

