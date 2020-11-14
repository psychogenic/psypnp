'''

Translates a set of feeds on the workspace.  Runs roughshod over the 
the last hole locations, so be wary.


This is mostly useful for unified sets of strip feeders, e.g. a 3d
printed set of n 8mm feeds, all name similarly (e.g. 8mmLeft_01, 
8mmLeft_02, etc).

Assumptions are thus:
 * it makes sense to move all of these together
 * they've been somewhat configured, namely that the first matching
   feed will be used to figure out the rough orientation of the strip
   and all subsequently processed feeders in this set will wind up 
   "pointing" in the same direction (by twiddling the last hole location).

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


def main():
    feeders_translate()
    

def feeders_translate():
    matchingFeeders = get_feeders_by_name()
    if matchingFeeders is None or not len(matchingFeeders):
        return 
    
    xMoveDistance = psypnp.ui.getUserInputFloat("X displacement", 0.0)
    yMoveDistance = psypnp.ui.getUserInputFloat("Y displacement", 0.0)
    
    if xMoveDistance == 0 and yMoveDistance == 0:
        return 
    
    fd1 = matchingFeeders[0]
    
    refHole = fd1.getReferenceHoleLocation()
    lastHole = fd1.getLastHoleLocation()
    
    orientationDist = lastHole.subtract(refHole)
    
    deltaX = 0.0
    deltaY = 0.0
    if abs(orientationDist.getX()) > abs(orientationDist.getY()):
        deltaX = orientationDist.getX()
    else:
        deltaY = orientationDist.getY() 
        
    
    displacementLocation = Location(refHole.getUnits(), 
                                    xMoveDistance,
                                    yMoveDistance,
                                    0,
                                    0)
    
    cleanOrientationDisp = Location(refHole.getUnits(), deltaX, deltaY, 0, 0)
    
    numChanged = 0
    for afeed in matchingFeeders:
        refHole = afeed.getReferenceHoleLocation()
        
        newLocRefHole = refHole.add(displacementLocation)
        newLastHole = newLocRefHole.add(cleanOrientationDisp)
        
        afeed.setReferenceHoleLocation(newLocRefHole)
        afeed.setLastHoleLocation(newLastHole)
        numChanged += 1
        

    psypnp.showMessage("Moved %i feeders" % numChanged)

                    
def get_feeders_by_name():
    
    nvStore = psypnp.nv.NVStorage('fdrs_align')
    
    # get last name used, if possible
    defName = nvStore.feedname
    if defName is None or not len(defName):
        defName = '8mmLeft' # some default value
    
    pname = psypnp.getUserInput("Common string in name of feeders in set", defName)
    if pname is None or not len(pname):
        return
    
    # stash it for next time
    nvStore.feedname = pname 
    
    matchingFeeders = []
    
    for afeeder in machine.getFeeders():
        if pname == '*' or afeeder.getName().find(pname) >= 0:
            matchingFeeders.append(afeeder)
    
    if not len(matchingFeeders):
        psypnp.ui.showError("No feeders match name '%s'" % pname)
        return None 
    
    return matchingFeeders


  

main()
