'''
Feeders position: move all feeds matching name to a given position
Options:
  - at camera 
  - at nozzle position

Assuming you have a feedset comprised of 
8mmLeft_01
8mmLeft_02
8mmLeft_03
...

If you specify "8mmLeft" the script will position the 
first (alpha sort) exactly at the position, and all others that match
relative to that (such that it shouldn't affect orientation or 
relative distance between feeds)


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
import psypnp.ui
import psypnp.search
import psypnp.nv 
import psypnp.config.storagekeys
import psypnp.debug 
import traceback


def main():
    sel = psypnp.ui.getOption('Position Feed(s)', 
                              'Position matching feeds relative to',
                              ['Camera position', 'Coordinates', 'Cancel'], 'Cancel')
    
    psypnp.debug.out.flush("SEL IS %s" % sel)
    if sel is None or sel < 0 or sel == 2:
        return
    
    
    matchingFeeds = get_feeders_by_name('Feed/set name or substring thereof')
    if matchingFeeds is None:
        # aborted 
        return 
    
    pos = None 
    if sel == 0:
        pos = get_camera_position()
    elif sel == 1:
        pos = get_user_coordinates()
        
    if pos is None or not len(pos) >= 2:
        return
    
    
    if not len(matchingFeeds):
        psypnp.ui.showError('No matching feeds found', '404')
        return
    
    
    num_moved = position_feeds(matchingFeeds, pos)
    if not num_moved:
        psypnp.ui.showError('Nothing moved?')
    elif num_moved == 1:
        psypnp.ui.showMessage('Feed repositioned.', 'Move Done')
    else:
        psypnp.ui.showMessage('Repositioned %i feeds.' % num_moved, 'Move Done')
        
    
def shift_feed(aFeed, displacementLocation):
        refHole = aFeed.getReferenceHoleLocation()
        lastHole = aFeed.getLastHoleLocation()
        newLocRefHole = refHole.add(displacementLocation)
        newLastHole = lastHole.add(displacementLocation)
        aFeed.setReferenceHoleLocation(newLocRefHole)
        aFeed.setLastHoleLocation(newLastHole)
        return True
        
        
def position_feeds(matchingFeeds, pos):
    psypnp.debug.out.buffer('Positioning feeds around %s' % str(pos))
    
    px = pos[0]
    py = pos[1]
    
    anchorFeed = matchingFeeds[0]
    anchorPosition = anchorFeed.getReferenceHoleLocation()
    
    posDeltaX = px - anchorPosition.getX()
    posDeltaY = py - anchorPosition.getY()
    
    
    displacementLoc = Location(anchorPosition.getUnits(), 
                                    posDeltaX,
                                    posDeltaY,
                                    0,
                                    0)
    
    psypnp.debug.out.buffer('Requested move to (%i,%i)' % (px, py))
    psypnp.debug.out.flush('Will displace all matching by (%s)' % str(displacementLoc))
    
    num_moved = 0
    for aFeed in matchingFeeds:
        psypnp.debug.out.buffer('Shifting feed %s' % str(aFeed))
        if shift_feed(aFeed, displacementLoc):
            num_moved += 1
            
    
    return num_moved
    



def get_camera_position():
    cam = machine.defaultHead.defaultCamera
    curloc = cam.getLocation()
    return (curloc.getX(), curloc.getY())

def get_user_coordinates():

    xval = psypnp.ui.getUserInputFloat("X", 0)
    if xval is None:
        # cancel
        return None
    yval = psypnp.ui.getUserInputFloat("Y", 0)
    if yval is None:
        # cancel
        return None
    
    return (xval, yval)

     
def get_feeders_by_name(promptstr):    
    nvStore = psypnp.nv.NVStorage(psypnp.config.storagekeys.FeedSearchStorage)
    # get last name used, if possible
    
    
    selFeeders = psypnp.ui.getSelectedFeeders()
    
    defName = nvStore.feedname
    if len(selFeeders) == 1:
        defName = selFeeders[0]
        
    if defName is None or not len(defName):
        defName = '8mmLeft' # some default value
    
    
    feedSearch = psypnp.search.prompt_for_feeders_by_name(promptstr, defName)
    
    if feedSearch is None or not len(feedSearch.searched):
        return None # aborted
    
    # stash it for next time
    nvStore.feedname = feedSearch.searched 
    
    return feedSearch.results



try:
    main()
except:
    print(traceback.format_exc())
