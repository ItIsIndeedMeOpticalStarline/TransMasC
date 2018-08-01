# The purpose of this program is to glue together the entire Doom2 Master Levels, into a single WAD.
# The program requires the omgifol library and it needs to be in the same directory as all Doom2 Master Levels WADs.

from omg import *
import glob

# Get all wads, in the order specified here: http://doom.wikia.com/wiki/Master_Levels_for_Doom_II
wad1 = WAD("ATTACK.WAD")
wad2 = WAD("CANYON.WAD")
wad3 = WAD("CATWALK.WAD")
wad4 = WAD("COMBINE.WAD")
wad5 = WAD("FISTULA.WAD")
wad6 = WAD("GARRISON.WAD")
wad7 = WAD("MANOR.WAD")
wad8 = WAD("PARADOX.WAD")
wad9 = WAD("SUBSPACE.WAD")
wad10 = WAD("SUBTERRA.WAD")
wad11 = WAD("TTRAP.WAD")
wad12 = WAD("VIRGIL.WAD")
wad13 = WAD("MINOS.WAD")
wad14 = WAD("BLOODSEA.WAD")
wad15 = WAD("MEPHISTO.WAD")
wad16 = WAD("NESSUS.WAD")
wad17 = WAD("GERYON.WAD")
wad18 = WAD("VESPERAS.WAD")
wad19 = WAD("BLACKTWR.WAD")
wad20 = WAD("TEETH.WAD")

# Now stuff all maps in wad1:
wad1.maps["MAP02"] = wad2.maps["MAP01"]
wad1.maps["MAP03"] = wad3.maps["MAP01"]
wad1.maps["MAP04"] = wad4.maps["MAP01"]
wad1.maps["MAP05"] = wad5.maps["MAP01"]
wad1.maps["MAP06"] = wad6.maps["MAP01"]
wad1.maps["MAP07"] = wad7.maps["MAP01"]
wad1.maps["MAP08"] = wad8.maps["MAP01"]
wad1.maps["MAP09"] = wad9.maps["MAP01"]
wad1.maps["MAP10"] = wad10.maps["MAP01"]
wad1.maps["MAP11"] = wad11.maps["MAP01"]
wad1.maps["MAP12"] = wad12.maps["MAP03"]
wad1.maps["MAP13"] = wad13.maps["MAP05"]
wad1.maps["MAP14"] = wad14.maps["MAP07"]
wad1.maps["MAP15"] = wad15.maps["MAP07"]
wad1.maps["MAP16"] = wad16.maps["MAP07"]
wad1.maps["MAP17"] = wad17.maps["MAP08"]
wad1.maps["MAP18"] = wad18.maps["MAP09"]
wad1.maps["MAP19"] = wad19.maps["MAP25"]
wad1.maps["MAP20"] = wad20.maps["MAP31"]

# And finally save:
wad1.to_file("doom_master_levels.wad")
print("Results saved to: doom_master_levels.wad")
