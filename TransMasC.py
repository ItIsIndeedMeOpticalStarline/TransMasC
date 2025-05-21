import os
import struct
import sys

def usage_and_quit():
    print('TransMasC: Command line script to merge Master Levels WADs into one file\n'
          '\n'
          'Usage: python TransMasC.py [options]\n'
          '\n'
          'Options:\n'
          '  -h | --help           Display this screen\n'
          '  --master-path <path>  Path to Master Levels WAD directory [default: \'.\']\n'
          '  --no-umapinfo         Do not add UMAPINFO to resulting WAD\n')
    quit(2)

def parse_args(argv: list[str]) -> tuple[str, bool]:
    masterPath: str = os.curdir
    noUMapInfo: bool = False

    for i in range(1, len(argv)):
        if argv[i] == '--help' or argv[i] == '-h':
            usage_and_quit()
        elif argv[i] == '--master-path':
            if masterPath != os.curdir or i >= len(argv): # Did we specify masterPath twice? Did we not specify it at all?
                usage_and_quit()
            
            i += 1
            masterPath = argv[i]
        elif argv[i] == '--no-umapinfo':
            noUMapInfo = True
        elif i - 1 < 1 or argv[i - 1] != '--master-path': # Was the previous argument expecting a path?
            usage_and_quit()

    return (masterPath, noUMapInfo)

WAD_INFO: list[tuple[str, list[list[str]]]] = [
    ("ATTACK.WAD", [["MAP01"]]),
    ("BLACKTWR.WAD", [["MAP25", "MAP19"]]),
    ("BLOODSEA.WAD", [["MAP07", "MAP14"]]),
    ("CANYON.WAD", [["MAP01", "MAP02"]]),
    ("CATWALK.WAD", [["MAP01", "MAP03"]]),
    ("COMBINE.WAD", [["MAP01", "MAP04"], ["RSKY1", "COMBSKY"]]),
    ("FISTULA.WAD", [["MAP01", "MAP05"]]),
    ("GARRISON.WAD", [["MAP01", "MAP06"]]),
    ("GERYON.WAD", [["MAP08", "MAP17"], ["RSKY1", "SLEEPSKY"]]),
    ("MANOR.WAD", [["MAP01", "MAP07"], ["STARS", "TITANSKY"]]),
    ("MEPHISTO.WAD", [["MAP07", "MAP15"]]),
    ("MINOS.WAD", [["MAP05", "MAP13"]]),
    ("NESSUS.WAD", [["MAP07", "MAP16"]]),
    ("PARADOX.WAD", [["MAP01", "MAP08"]]),
    ("SUBSPACE.WAD", [["MAP01", "MAP09"]]),
    ("SUBTERRA.WAD", [["MAP01", "MAP10"]]),
    ("TEETH.WAD", [["MAP31", "MAP20"], ["MAP32", "MAP21"]]),
    ("TTRAP.WAD", [["MAP01", "MAP11"]]),
    ("VESPERAS.WAD", [["MAP09", "MAP18"]]),
    ("VIRGIL.WAD", [["MAP03", "MAP12"]]),
    ("ml_midipack_crispydoom.wad", 
        [
            ["TITLEPIC"], ["INTERPIC"], ["TRAKLIST"], ["D_RUNNIN"], 
            ["D_STALKS"], ["D_COUNTD"], ["D_BETWEE"], ["D_DOOM"], 
            ["D_THE_DA"], ["D_SHAWN"], ["D_DDTBLU"], ["D_IN_CIT"],
            ["D_DEAD"], ["D_STLKS2"], ["D_THEDA2"], ["D_DOOM2"], 
            ["D_DDTBL2"], ["D_RUNNI2"], ["D_DEAD2"], ["D_STLKS3"], 
            ["D_ROMERO"], ["D_SHAWN2"], ["D_MESSAG"], ["D_COUNT2"],
            ["D_EVIL"], ["D_READ_M"], ["D_DM2INT"], ["D_DM2TTL"]
        ]
    )
]

# TODO: Returning if we found the MIDI Pack is kinda unreadable and janky.
# TODO: There's no point in returning the whole dictionary though
def verify_wads(path: str) -> bool:
    wadsPresent: dict[str, bool] = { name : False for name, _, in WAD_INFO }
    foundMidiPack: bool = False

    for entry in os.scandir(path):
        if wadsPresent.__contains__(entry.name):
            wadsPresent[entry.name] = True
        if entry.name == 'ml_midipack_crispydoom.wad':
            print(f'LOG: Found {entry.name}, adding to final WAD file')
            foundMidiPack = True

    crashMe: bool = False
    for wadName, found in wadsPresent.items():
        if found != True:
            print(f'ERROR: Could not find WAD {wadName}', file=sys.stderr)
            crashMe = True

    if crashMe:
        exit(1)

    return foundMidiPack

def str_to_wad_str(string: str) -> bytes:
    paddedString: str = string
    if len(string) < 8:
        paddedString = string.ljust(8, '\x00') # Pad with null terminators

    try:
        return paddedString.encode('ascii')[:8] # Trim and do not null terminate
    except:
        print('ERROR: Improperly formed WAD file')
        exit(1)

INT32_SIZE: int = 4
FILE_LUMP_SIZE: int = 16

def extract_lump(wad: bytes, lumpName: str, newLumpName: str = '') -> tuple[bytes, bytes]:
    # We don't care about the WAD identification, so we skip the four byte identifier
    numberOfLumps: int = int.from_bytes(wad[4:(4 + INT32_SIZE)], 'little', signed = True)
    infoTableOffset: int = int.from_bytes(wad[(4 + INT32_SIZE):((4 + INT32_SIZE) + INT32_SIZE)], 'little', signed = True)

    index: int = 0
    for index in range(numberOfLumps):
        lumpOffset: int = infoTableOffset + (index * FILE_LUMP_SIZE)
        currentLumpName: bytes = wad[(lumpOffset + 4 + 4):((lumpOffset + 4 + 4) + 8)]
        if currentLumpName == str_to_wad_str(lumpName):
            lumpDataOffset: int = int.from_bytes(wad[lumpOffset:(lumpOffset + INT32_SIZE)], 'little', signed = True)
            lumpDataSize: int = int.from_bytes(wad[(lumpOffset + INT32_SIZE):((lumpOffset + INT32_SIZE) + INT32_SIZE)], 'little', signed = True)
            return (str_to_wad_str(newLumpName), wad[lumpDataOffset:(lumpDataOffset + lumpDataSize)])

    print(f'ERROR: WAD file did not contain the expected lump {lumpName}')
    exit(1)

# Code duplication but calling extract lump 11 times would have hurt my soul, and the performance
def extract_map(wad: bytes, mapName: str, newMapName: str = '') -> list[tuple[bytes, bytes]]:
    # We don't care about the WAD identification, so again, we skip it
    numberOfLumps: int = int.from_bytes(wad[4:(4 + INT32_SIZE)], 'little', signed = True)
    infoTableOffset: int = int.from_bytes(wad[(4 + INT32_SIZE):((4 + INT32_SIZE) + INT32_SIZE)], 'little', signed = True)

    LUMP_ORDER: list[str] = [ mapName, 'THINGS', 'LINEDEFS', 'SIDEDEFS', 'VERTEXES', 'SEGS', 'SSECTORS', 'NODES', 'SECTORS', 'REJECT', 'BLOCKMAP' ]
    mapLumps: list[tuple[bytes, bytes]] = []
    baseIndex: int = 0 
    for baseIndex in range(numberOfLumps):
        lumpOffset: int = infoTableOffset + (baseIndex * FILE_LUMP_SIZE)
        lumpName: bytes = wad[lumpOffset + INT32_SIZE * 2:lumpOffset + FILE_LUMP_SIZE]

        if lumpName == str_to_wad_str(mapName):
            expectedNextLumpIndex: int = 0
            for mapIndex in range(len(LUMP_ORDER)):
                mapLumpOffset: int = lumpOffset + (mapIndex * FILE_LUMP_SIZE)
                mapLumpName: bytes = wad[mapLumpOffset + INT32_SIZE * 2:mapLumpOffset + FILE_LUMP_SIZE]

                # This way of doing things has a redundant string comparison to mapName
                # It's more trouble than it's worth to get rid of it right now
                if mapLumpName == str_to_wad_str(LUMP_ORDER[expectedNextLumpIndex]):
                    lumpDataOffset: int = int.from_bytes(wad[mapLumpOffset:(mapLumpOffset + INT32_SIZE)], 'little', signed = True)
                    lumpDataSize: int = int.from_bytes(wad[(mapLumpOffset + INT32_SIZE):(mapLumpOffset + (INT32_SIZE * 2))], 'little', signed = True)
                    if mapLumpName == str_to_wad_str(mapName) and len(newMapName) > 0:
                        mapLumps.append((str_to_wad_str(newMapName), wad[lumpDataOffset:(lumpDataOffset + lumpDataSize)]))
                    else:
                        mapLumps.append((mapLumpName, wad[lumpDataOffset:(lumpDataOffset + lumpDataSize)]))
                    expectedNextLumpIndex += 1  
                else:
                    print(f'Could not find {LUMP_ORDER[expectedNextLumpIndex]} lump in WAD for map {mapName}')
                    exit(1)

                if expectedNextLumpIndex >= len(LUMP_ORDER): # Bail if we got all of the lumps we need
                    return mapLumps

    print(f'ERROR: WAD file did not contain the expected map {mapName}')
    exit(1)

def to_int_of_bitlength(i: int, bitlength: int) -> int:
    if (bitlength <= 0):
        return 0
    
    i &= ((1 << bitlength) - 1)    # Mask
    if i & (1 << (bitlength - 1)): # Overflow
        i -= (1 << bitlength)
    return i

def to_int32(i: int) -> int:
    return to_int_of_bitlength(i, 32)

def to_int16(i: int) -> int:
    return to_int_of_bitlength(i, 16)

def encode_int(i: int) -> bytes:
    return to_int32(i).to_bytes(4, 'little', signed = True)

def encode_short(i: int) -> bytes:
    return to_int16(i).to_bytes(2, 'little', signed = True)

def encode_pair_of_shorts(a: int, b: int) -> bytes:
    return ((to_int16(a) << 16) + to_int16(b)).to_bytes(4, 'little', signed = True)

def make_umapinfo(foundMidiPack: bool) -> str:
    #region UMAPINFO
    baseUmapinfo = '''MAP MAP01
{
    levelname = \"Attack\"
    label = clear
}

MAP MAP02
{
    levelname = \"Canyon\"
    label = clear
    music = \"D_RUNNIN\"
}

MAP MAP03
{
    levelname = \"The Catwalk\"
    label = clear
    music = \"D_RUNNIN\"
}

MAP MAP04
{
    levelname = \"The Combine\"
    label = clear
    music = \"D_RUNNIN\"
    skytexture = \"COMBSKY\"
}

MAP MAP05
{
    levelname = \"The Fistula\"
    label = clear
    music = \"D_RUNNIN\"
}

MAP MAP06
{
    intertext = clear
    levelname = \"The Garrison\"
    label = clear
    music = \"D_RUNNIN\"
}

MAP MAP07
{
    levelname = \"Titan Manor\"
    label = clear
    music = \"D_RUNNIN\"
    skytexture = \"TITANSKY\"
    bossaction = clear
}

MAP MAP08
{
    levelname = \"Paradox\"
    label = clear
    music = \"D_RUNNIN\"
}

MAP MAP09
{
    levelname = \"Subspace\"
    label = clear
    music = \"D_RUNNIN\"
}

MAP MAP10
{
    levelname = \"Subterra\"
    label = clear
    music = \"D_RUNNIN\"
}

MAP MAP11
{
    intertext = clear
    levelname = \"Trapped On Titan\"
    label = clear
    music = \"D_RUNNIN\"
    skytexture = \"TITANSKY\"
}

MAP MAP12
{
    levelname = \"Virgil's Lead\"
    label = clear
    music = \"D_COUNTD\"
    skytexture = \"SLEEPSKY\"
}

MAP MAP13
{
    levelname = \"Minos' Judgement\"
    label = clear
    music = \"D_DOOM\"
    skytexture = \"SLEEPSKY\"
}

MAP MAP14
{
    levelname = \"Bloodsea Keep\"
    label = clear
    music = \"D_SHAWN\"
    skytexture = \"SKY1\"
    bossaction = Fatso, 23, 666
    bossaction = Arachnotron, 30, 667
}

MAP MAP15
{
    levelname = \"Mephisto's Maosoleum\"
    label = clear
    music = \"D_SHAWN\"
    skytexture = \"SKY1\"
    bossaction = Fatso, 23, 666
    bossaction = Arachnotron, 30, 667
}

MAP MAP16
{
    levelname = \"Nessus\"
    label = clear
    music = \"D_SHAWM\"
    skytexture = \"SLEEPSKY\"
    bossaction = Fatso, 23, 666
    bossaction = Arachnotron, 30, 667
}

MAP MAP17
{
    levelname = \"Geryon\"
    label = clear
    music = \"D_DDTBLU\"
    skytexture = \"SLEEPSKY\"
}

MAP MAP18
{
    levelname = \"Vesperas\"
    label = clear
    music = \"D_IN_CIT\"
    skytexture = \"SLEEPSKY\"
}

MAP MAP19
{
    levelname = \"Black Tower\"
    label = clear
    music = \"D_ADRIAN\"
    skytexture = \"SKY3\"
}

MAP MAP20
{
    intertext = clear
    levelname = \"The Express Elevator To Hell\"
    label = clear
    music = \"D_EVIL\"
    next = \"MAP30\"
    nextsecret = \"MAP21\"
    skytexture = \"SKY3\"
}

MAP MAP21
{
    levelname = \"Bad Dream\"
    label = clear
    music = \"D_ULTIMA\"
    next = \"MAP30\"
    skytexture = \"SKY3\"
}'''
    #endregion

    if foundMidiPack:
        editedUMapInfo: str = ''
        for line in baseUmapinfo.splitlines(True):
            if not line.startswith('    m'): # No need to compare more characters than just '   m' to know if it's the music key
                editedUMapInfo += line

        return editedUMapInfo
    
    return baseUmapinfo

# This is practically all hardcoded but really it doesn't need to be fancy
def make_pnames_and_texturex() -> tuple[bytes, bytes]:
    NUM_OF_PATCHES = 3
    outputPNamesBytes: bytes = encode_int(NUM_OF_PATCHES) + str_to_wad_str('TITANSKY') + str_to_wad_str('COMBSKY') + str_to_wad_str('SLEEPSKY')

    # Format for each texture is as follows:
    # 8 byte identifying string
    # 4 bytes unused
    # 2 byte texture width
    # 2 byte texture height
    # 4 bytes unused
    # 2 byte number of patches
    # 10 bytes per specified number of patches
    #   Format for each patch is as follows:
    #   2 byte x position
    #   2 byte y position
    #   2 byte pname number
    #   4 bytes unused

    mapTextures: list[bytes] = [
        (
            str_to_wad_str('TITANSKY') + encode_int(0) + encode_pair_of_shorts(1024, 128) + encode_int(0) + encode_short(4) # Texture
                + encode_pair_of_shorts(0, 0) + encode_short(0) + encode_pair_of_shorts(0, 0) # Patches
                + encode_pair_of_shorts(256 * 1, 0) + encode_short(0) + encode_int(0)
                + encode_pair_of_shorts(256 * 2, 0) + encode_short(0) + encode_int(0)
                + encode_pair_of_shorts(256 * 3, 0) + encode_short(0) + encode_int(0)
        ),
        (
            str_to_wad_str('COMBSKY') + encode_int(0) + encode_pair_of_shorts(256, 128) + encode_int(0) + encode_short(1) # Texture
                + encode_pair_of_shorts(0, 0) + encode_short(1) + encode_int(0) # Patch
        ),
        (
            str_to_wad_str('SLEEPSKY') + encode_int(0) + encode_pair_of_shorts(256, 128) + encode_int(0) + encode_short(1) # Texture
                + encode_pair_of_shorts(0, 0) + encode_short(2) + encode_int(0) # Patch
        )
    ]

    NUM_OF_TEXTURES = 3
    outputTextureXBytes: bytes = encode_int(NUM_OF_TEXTURES) + encode_int(0) + encode_int(0 + len(mapTextures[0])) + encode_int(0 + len(mapTextures[0]) + len(mapTextures[1]))

    for mapTexture in mapTextures:
        outputTextureXBytes += mapTexture

    return (outputPNamesBytes, outputTextureXBytes)

def make_wad(outputLumps: list[tuple[bytes, bytes]]) -> bytes:
    wadData: bytearray = bytearray(b'')
    totalLumpDataSegmentSize: int = 0
    for _, lumpData in outputLumps:
        wadData += lumpData
        totalLumpDataSegmentSize += len(lumpData)

    outputWadIdentifier: bytes = str_to_wad_str('PWAD')
    headerSize: int = len(outputWadIdentifier) + INT32_SIZE * 2  
    # Format for header is as follows:
    # 4 byte identifying string
    # 4 byte number of lumps
    # 4 byte offset to lump data
    outputWadBytes: bytearray = outputWadIdentifier + encode_int(len(outputLumps)) + encode_int(headerSize) + wadData

    # Write the directory
    FIRST_PATCH_LUMP_NAME, LAST_PATCH_LUMP_NAME = str_to_wad_str('TITANSKY'), str_to_wad_str('SLEEPSKY')
    currentLumpDataOffset: int = headerSize
    for lumpName, lumpData in outputLumps:
        if (lumpName == FIRST_PATCH_LUMP_NAME):
            outputWadBytes += encode_int(0) + encode_int(0) + str_to_wad_str('PP_START') # Add virtual lump before graphics patches

        currentLumpDataSize = len(lumpData)
        outputWadBytes += encode_int(currentLumpDataOffset) + encode_int(currentLumpDataSize) + lumpName # Add directory entry
        currentLumpDataOffset += currentLumpDataSize

        if (lumpName == LAST_PATCH_LUMP_NAME):
            outputWadBytes += encode_int(0) + encode_int(0) + str_to_wad_str('PP_END') # Close PP_START

    return bytes(outputWadBytes)

if __name__ == '__main__':
    path: str
    noUMapInfo: bool 
    path, noUMapInfo = parse_args(sys.argv)

    foundMidiPack: bool = verify_wads(path)

    outputLumps: list[tuple[bytes, bytes]] = []
    WAD_HEADER_SIZE: int = 12
    for name, lumpsToExtract in WAD_INFO:
        if not foundMidiPack and name == "ml_midipack_crispydoom.wad":
            continue

        with open(path + os.sep + name, 'rb') as wadFile:
            data = wadFile.read()

            if len(data) < WAD_HEADER_SIZE:
                print('ERROR: File named as a WAD was not a WAD file')
                exit(1)

            for lump in lumpsToExtract:
                lumpName: str = lump[0]
                newLumpName: str = ''
                if (len(lump) > 1):
                    newLumpName = lump[1]

                if lumpName.startswith('MAP'):
                    for lump in extract_map(data, lumpName, newLumpName):
                        outputLumps.append(lump)
                else:
                    outputLumps.append((extract_lump(data, lumpName, newLumpName)))

    if not noUMapInfo:
        outputLumps.append((str_to_wad_str('UMAPINFO'), make_umapinfo(foundMidiPack).encode('ascii')))

    pnamesData: bytes
    textureXData: bytes
    pnamesData, textureXData = make_pnames_and_texturex()
    outputLumps.append((str_to_wad_str('PNAMES'), pnamesData))
    outputLumps.append((str_to_wad_str('TEXTURE1'), textureXData))

    wad: bytes = make_wad(outputLumps)

    OUTPUT_FILE_PATH = path + os.sep + 'The Master Levels.wad'
    if os.path.isfile(OUTPUT_FILE_PATH): # Let's not override any files if we can help it...
        print(f'ERROR: The Master Levels.wad already exists in {path}')
        exit(1)

    with open(OUTPUT_FILE_PATH, 'wb') as outputFile:
        outputFile.write(wad)

    print('LOG: Process was successful')