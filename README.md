# TransMasC
The Mater Levels for Doom 2 are usually distributed as 20 separate WAD files.

This script:
 - Combines all 21 Master Levels into one WAD (The Master Levels for Doom II.wad).
 - Optionally adds a UMAPINFO lmp to the resulting WAD, so that all levels using map specific tags work correctly.
 - Optionally combines Peter Lawrence's Master Levels for Doom II - 25th Anniversary MIDI Pack with the resulting WAD.

# Prerequisites
None other than Python! Grab and go.

# Usage
Put TransMasC.py in the same directory as the 20 Master Levels WADs, (and optionally the MIDI Pack,) and run:

REMARK: commands in square brackets indicate an optional argument.

python TransMasC.py [--help] [--master-path] [--no-umapinfo]

The result will be saved in a file called The Master Levels.wad.