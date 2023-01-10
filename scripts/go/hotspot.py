'''

Add/delete and use "hotspot" locations: places of interest and use within
the work area.

Add and name hotspots, and they'll appear in the list.  Click "Go XYZ" and 
the default camera will head there (at a safez).

Will only move things if 
  psypnp.should_proceed_with_motion
says we're good to go.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

@author: Pat Deegan
@copyright: Copyright (C) 2023 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

############## BOILER PLATE #################
# submitUiMachineTask should be used for all code that interacts
# with the machine. It guarantees that operations happen in the
# correct order, and that the user is presented with a dialog
# if there is an error.
from org.openpnp.util.UiUtils import submitUiMachineTask
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


#from __future__ import absolute_import, division

from org.openpnp.model import LengthUnit, Location
from org.openpnp.util import MovableUtils
import psypnp.ui
import psypnp.debug
import psypnp.user_config as user_prefs
from psypnp import should_proceed_with_motion


_scriptStorage = None 
DestinationLocation = None 
def getNVStore():
    global _scriptStorage
    if _scriptStorage is None:
        _scriptStorage = psypnp.nv.NVStorage('go_hotspot')
        if _scriptStorage.hotspots is None:
            _scriptStorage.hotspots = dict() 
            
    return _scriptStorage

def configuredHotspotNames():
    return list(reversed(sorted(getNVStore().hotspots.keys())))
    

def main():
    
    global DestinationLocation
    if machine.getDefaultHead() is None:
        # too weird
        psypnp.ui.showError("No default head??")
        return False
    
    cam = machine.getDefaultHead().getDefaultCamera()
    if cam is None:
        psypnp.ui.showError("No default cam??")
        return False
        
    
    nvStore = getNVStore()
    
    
    options = ['Cancel', 'Add']
    hotSpotNames = configuredHotspotNames()
    if len(hotSpotNames):
        options.append('Delete')
        for hsName in hotSpotNames:
            options.append('Go %s' % hsName)
            
            
    
    
    val = psypnp.ui.getOption("Hotspots", 
                "Select action for location 'hotspots'",
                options)

    if val is None or val == 0:
        return False
    if val == 1:
        add_hotspot()
        return True 
    if val == 2:
        # delete 
        delete_hotspot()
        return True 
    
    hsIndex = val - 3
    if hsIndex < 0 or hsIndex >= len(hotSpotNames):
        psypnp.ui.showError("Something not right.")
        return False
    
    selHotspotName = hotSpotNames[hsIndex]
    if selHotspotName not in nvStore.hotspots:
        psypnp.ui.showError("Something not right, unknown hotspot %s" % selHotspotName)
        return False
        
    hotSpot = nvStore.hotspots[selHotspotName]
    camLoc = cam.getLocation()
    DestinationLocation = Location(camLoc.getUnits(), hotSpot['x'], hotSpot['y'], camLoc.getZ(), camLoc.getRotation())
    
    psypnp.debug.out.flush(str(DestinationLocation))
    if should_proceed_with_motion():
       submitUiMachineTask(go_cam)
    
    return user_prefs.gohotspots_loopuntilcancel

def delete_hotspot():
    
    nvStore = getNVStore()

    options = ['Cancel']
    
    hotSpotNames = configuredHotspotNames()
    if len(hotSpotNames):
        for hsName in hotSpotNames:
            options.append(hsName)
    val = psypnp.ui.getOption("Delete Hotspot", 
                "Delete saved hotspot",
                options
                );
    if val is None or val == 0:
        return
    
    hsToDel = hotSpotNames[val - 1]
    if hsToDel in nvStore.hotspots:
        del nvStore.hotspots[hsToDel]
        nvStore.saveAll()
    return
    
def add_hotspot():
    val = psypnp.ui.getOption("Add Hotspot", 
                "Add for current location",
                ['Cancel', '@ Camera', '@ Nozzle']);
                
    curLoc = None 
    if val == 0:
        return 

    if val == 1:
        # camera
        cam = machine.defaultHead.getDefaultCamera()
        if cam is None:
            psypnp.ui.showError("Can't get default cam??")
            return 
        curLoc = cam.getLocation()
    elif val == 2:
        noz = machine.defaultHead.getDefaultNozzle()
        if noz is None:
            psypnp.ui.showError("Can't get default noz??")
            return 
        curLoc = noz.getLocation()
        
    if curLoc is None:
        psypnp.ui.showError("Somehow don't have a location specified?")
        return 
        
    nvStore = getNVStore()
    defName = nvStore.lastspot
    if defName is None:
        defName = 'MyFaveHotspot'
    locName = psypnp.ui.getUserInput('Hotspot designation', defName)
    if locName is None or not len(locName):
        return 
    
    nvStore.lastspot = locName 
    nvStore.hotspots[locName] = {
        'u': curLoc.getUnits().shortName,
        'x': curLoc.getX(),
        'y': curLoc.getY()
        }
    nvStore.saveAll()
    

def go_nozzle():
    global DestinationLocation
    
    if DestinationLocation is None:
        psypnp.ui.showError("No location set?")
        return # should error
    
    if machine.defaultHead is None:
        # too weird
        psypnp.ui.showError("No default head??")
        return
    
    defNozz = machine.defaultHead.getDefaultNozzle()
    if defNozz is None:
        psypnp.ui.showError("Can't get default nozzle??")
        return
    
    
    MovableUtils.moveToLocationAtSafeZ(defNozz, DestinationLocation)
    
def go_cam():
    global DestinationLocation
    
    if DestinationLocation is None:
        psypnp.ui.showError("No location set?")
        return # should error
    
    if machine.defaultHead is None:
        # too weird
        psypnp.ui.showError("No default head??")
        return
    
    cam = machine.defaultHead.defaultCamera
    if cam is None:
        psypnp.ui.showError("Can't get default cam??")
        return # should error
    
    MovableUtils.moveToLocationAtSafeZ(cam, DestinationLocation)

doContinue = True 
while doContinue:
    doContinue = main()
