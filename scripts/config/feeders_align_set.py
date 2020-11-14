'''
Attempt to align all the reference hole locations for feeders in a set.

Assumes that feeders can be grouped based on their name/id.  For instance,
if you have a set of reference strip feeders grouped in some physical way
and named rationally (e.g. 12mmLeft_01, 12mmLeft_02, ... 12mmLeft_12), and
they have been placed on the workspace at some point so they're positions
are a loose reflection of reality:

      12mmLeft_01 *
    12mmLeft_02 *
        12mmLeft_03 *
      12mmLeft_04 *
   12mmLeft_05 *
      12mmLeft_06 *
    12mmLeft_07 *
    12mmLeft_08 *
    ...

This script will figure out that they are roughly aligned vertically, and 
reposition them to get:

      12mmLeft_01 *
      12mmLeft_02 *
      12mmLeft_03 *
      12mmLeft_04 *
      12mmLeft_05 *
      12mmLeft_06 *
      12mmLeft_07 *
      12mmLeft_08 *
       ...

@note: assumes some basic alignment already configured, and that they are 
either aligned vertically or horizontally.

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
    feeders_align()
    
def updatePosStats(existingAggregate, newValue):
    (sampCount, mean, M2) = existingAggregate
    sampCount += 1
    delta = newValue - mean
    mean += delta / sampCount
    delta2 = newValue - mean
    M2 += delta * delta2
    return (sampCount, mean, M2)

# Retrieve the mean, variance and sample variance from an aggregate
def finalizePosStats(existingAggregate):
    (sampCount, mean, M2) = existingAggregate
    if sampCount < 2:
        return float("nan")
    else:
        (mean, variance, sampleVariance) = (mean, M2 / sampCount, M2 / (sampCount - 1))
        return (mean, variance, sampleVariance)
    

def feeders_align():
    matchingFeeders = get_feeders_by_name()
    if matchingFeeders is None or not len(matchingFeeders):
        return 
    
    feedLocations = []
    
    runningStatsX = (0,0,0)
    runningStatsY = (0,0,0)
    for afeeder in matchingFeeders:
        if afeeder.isEnabled():
            refHole = afeeder.getReferenceHoleLocation()
            if refHole is None or not refHole:
                print("A feed has no reference hole... hum")
            else:
                runningStatsX = updatePosStats(runningStatsX, refHole.getX())
                runningStatsY = updatePosStats(runningStatsY, refHole.getY())
    
    if runningStatsX[0] < 2:
        # enabled count is too low
        psypnp.ui.showError("Not enough enabled feeds to reliably find pos")
        return 
    
    statsX = finalizePosStats(runningStatsX)
    statsY = finalizePosStats(runningStatsY)
    
    print("Final stats: \nX: %s\n\nY: %s" % (statsX, statsY))
    targetX = None 
    targetY = None 
    if statsX[1] < statsY[1]:
        # is a vertical set
        targetX = statsX[0] # set to average X
        if not psypnp.ui.getConfirmation(
            "Effect change?",
            "Will move vertical set to align with x=%s. Proceed?" % str(targetX)
        ):
            return 
    else:
        targetY = statsY[0] # set to average Y
        if not psypnp.ui.getConfirmation(
            "Effect change?",
            "Will move horizontal set to align with y=%s. Proceed?" % str(targetY)
        ):
            return 
        
        
    numChanged = 0
    for afeeder in matchingFeeders:
        refHole = afeeder.getReferenceHoleLocation()
        if targetX is not None:
            newX = targetX
            newY = refHole.getY()
        elif targetY is not None:
            newX = refHole.getX()
            newY = targetY 
        newLoc = Location(refHole.getUnits(), newX, newY, refHole.getZ(), refHole.getRotation())
        print("Setting feeder loc to: %s" % str(newLoc))
        
        numChanged += 1
        afeeder.setReferenceHoleLocation(newLoc)
        
    
    gui.getFeedersTab().repaint()
    psypnp.showMessage("Aligned %i feeders" % numChanged)
        
        
                    
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
    
    if len(matchingFeeders) < 2:
        psypnp.ui.showError("Only a single feeder named '%s'" % pname)
        return None 
    
    return matchingFeeders




main()
