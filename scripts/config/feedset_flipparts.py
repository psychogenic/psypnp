'''

Migrates the contents of one feedset to another.

This is mostly (only) useful for unified sets of strip feeders, e.g. a 3d
printed set of n 8mm feeds, all name similarly (e.g. 8mmLeft_01, 
8mmLeft_02, etc).

So, if you swap
 8mmLeft_
for 
 8mmTop_
then
 the part in 8mmLeft_01 will be put into 8mmTop_01,
 the part in 8mmLeft_02 will be put into 8mmTop_02,
etc.
If EnableSwap is True (below, True by default) then the 
parts and settings from the destination are swapped back
to the source, otherwise it's a one-way deal.
 
@note: Short version is this is to be used early on in your setup process, and 
the feeders will need to be "auto-setup" after usage.

@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

############## BOILER PLATE #################
# boiler plate to get access to psypnp modules, outside scripts/ dir
import os.path
import sys
python_scripts_folder = os.path.join(scripting.getScriptsDirectory().toString(),
                                      '..', 'lib')
sys.path.append(python_scripts_folder)

# setup globals for modules
import psypnp.globals
psypnp.globals.setup(machine, config, scripting, gui)

############## /BOILER PLATE #################

from org.openpnp.model import Location, Length, LengthUnit 

import psypnp
import psypnp.nv
import psypnp.config.storagekeys
from psypnp.project.feed_manager import FeedSwapper

EnableSwap = True # sends dest info back to source


def main():
    feedset_contents_migrate()
    

def feedset_contents_migrate():
    matchingFeedersFrom = get_feeders_by_name('Substring of feed names to flip')
    if matchingFeedersFrom is None or not len(matchingFeedersFrom):
        return 
    numModded = 0
    fswap = FeedSwapper()
    numFeeds = len(matchingFeedersFrom)
    halfNumFeeds =  numFeeds// 2
    maxIdx = numFeeds - 1
    
    if halfNumFeeds < 1:
        psypnp.ui.showError("nuttin' to do.")
        return
    
    for i in range(0, halfNumFeeds):
        srcFeed = matchingFeedersFrom[i]
        destFeed = matchingFeedersFrom[maxIdx - i]
        
        fswap.movePart(srcFeed, destFeed, True)
            
        numModded += 1

    psypnp.showMessage("Flipped %i feeders" % numModded)



def get_feeders_by_name(promptstr):    
    
    nvStore = psypnp.nv.NVStorage(psypnp.config.storagekeys.FeedSearchStorage)
    # get last name used, if possible
    defName = nvStore.feedname
    
    if defName is None or not len(defName):
        defName = '8mmLeft' # some default value
    
    
    feedSearch = psypnp.search.prompt_for_feeders_by_name(promptstr, defName)
    
    if feedSearch is None or not len(feedSearch.searched):
        return # aborted
    
    # stash it for next time
    nvStore.feedname = feedSearch.searched 
    
    return feedSearch.results


main()
