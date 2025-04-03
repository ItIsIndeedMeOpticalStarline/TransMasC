import os
import fileinput
import sys

def usage():
    print('TransMasC: Command line script to merge Master Levels WADs into one file\n'
          '\n'
          'Usage: python TransMasC.py [options]\n'
          '\n'
          'Options:\n'
          '  -h | --help           Display this screen\n'
          '  --master-path <path>  Path to Master Levels WAD directory [default: \'.\']\n'
          '  --no-umapinfo         Do not add UMAPINFO to resulting WAD\n')
    quit(2)

PRINT_USAGE_ONLY: tuple[bool, str, bool] = (True, '', False)

def parse_args(argv: list[str]) -> tuple[bool, str, bool]:
    masterPath: str = os.curdir
    noUMapInfo: bool = False

    for i in range(1, len(argv)):
        if argv[i] == '--help' or argv[i] == '-h':
            return PRINT_USAGE_ONLY
        elif argv[i] == '--master-path':
            if masterPath != os.curdir or i >= len(argv): # Did we specify masterPath twice? Did we not specify it at all?
                return PRINT_USAGE_ONLY
            
            i += 1
            masterPath = argv[i]
        elif argv[i] == '--no-umapinfo':
            noUMapInfo = True
        elif i - 1 < 1 or argv[i - 1] != '--master-path': # Was the previous argument expecting a path?
            usage()

    return (False, masterPath, noUMapInfo)

WAD_NAMES: list[str] = [
    "ATTACK.WAD", 
    "BLACKTWR.WAD",
    "BLOODSEA.WAD",
    "CANYON.WAD",
    "CATWALK.WAD",
    "COMBINE.WAD",
    "FISTULA.WAD",
    "GARRISON.WAD",
    "GERYON.WAD",
    "MANOR.WAD",
    "MEPHISTO.WAD",
    "MINOS.WAD",
    "NESSUS.WAD",
    "PARADOX.WAD",
    "SUBSPACE.WAD",
    "SUBTERRA.WAD",
    "TEETH.WAD",
    "TTRAP.WAD",
    "VESPERAS.WAD",
    "VIRGIL.WAD",
]

def verify_wads(path: str):
    wadsPresent: dict[str, bool] = { name : False for name in WAD_NAMES }

    for entry in os.scandir(path):
        if wadsPresent.__contains__(entry.name):
            wadsPresent[entry.name] = True

    crashMe: bool = False
    for wadName, found in wadsPresent.items():
        if found != True:
            print(f'ERROR: Could not find WAD {wadName}', file=sys.stderr)
            crashMe = True

    if crashMe:
        exit(1)

if __name__ == '__main__':
    printUsage: bool
    path: str
    noUMapInfo: bool 
    printUsage, path, noUMapInfo = parse_args(sys.argv)

    if printUsage:
        usage()

    verify_wads(path)
