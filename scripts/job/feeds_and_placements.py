'''
Enable feeders|placements based on placements|feeders

Allows you to mirror one side of setup to the other, e.g. disable 
all placements that don't have an enabled feeder for the part.


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

#from __future__ import absolute_import
import re
import psypnp
import psypnp.ui

from  org.openpnp.model.Placement import Type as PlacementType

def main():
    if select_action_and_perform():
        refresh_checkboxen()


def select_action_and_perform():
    
    val = psypnp.ui.getOption("Setup Mirror", 
                "Enable/disable feeds/placements based on corresponding setting",
                ['Feeders -> placements', 'Placements -> Feeders', 'Cancel'], 'Cancel')


    if val is None or val < 0 or val == 2:
        return False 
    
    
    boardsList = get_selected_boards()
    if boardsList is None:
        return False
    
    if val == 1:
        placements_to_feeders(boardsList)
    if val == 0:
        feeders_to_placements(boardsList)

    return True

def feeders_to_placements(boardsList):
    enabledFeederParts = get_enabled_feederparts_by_id()
    
    numEnabled = 0
    for aBoard in boardsList:
        for aplacement in aBoard.getPlacements():
            placePart = aplacement.getPart()
            if placePart is None:
                continue 
            if placePart.getId() in enabledFeederParts:
                aplacement.setEnabled(True)
                numEnabled += 1
            else:
                if aplacement.getType() != PlacementType.Fiducial: 
                    aplacement.setEnabled(False) 
    
    refresh_checkboxen()   
    if numEnabled:
        psypnp.ui.showMessage("Done. placements enabled: %i" % numEnabled)
    else:
        psypnp.ui.showMessage("Done. No placements enabled.")

    return True
    
    
    
def placements_to_feeders(boardsList):
    
    enabledParts = get_enabled_parts_by_id(boardsList)
    
    allFeeds = psypnp.search.get_sorted_feeders_list()
    numEnabled = 0
    for aFeed in allFeeds:
        fPart = aFeed.getPart()
        if fPart is None:
            aFeed.setEnabled(False)
            continue 
        if fPart.getId() in enabledParts:
            aFeed.setEnabled(True)
            numEnabled += 1
        else:
            aFeed.setEnabled(False)
        
        
    if numEnabled:
        psypnp.ui.showMessage("Done. No feeders enabled")
        return True 
        
    psypnp.ui.showMessage("Done.  Feeder enabled: %i" % numEnabled)
    return True 

def refresh_checkboxen():
    gui.jobTab.getJobPlacementsPanel().repaint()

def get_selected_boards():
    boardsList = psypnp.ui.getSelectedBoards()
    if boardsList is None or not len(boardsList):
        psypnp.ui.showError("Select at least one board")
        return None
    return boardsList


def get_enabled_parts_by_id(boardsList):
    enabledParts = dict()
    for aBoard in boardsList:
        for aplacement in aBoard.getPlacements():
            if aplacement.isEnabled():
                part = aplacement.getPart()
                if part is None:
                    continue 
                enabledParts[part.getId()] = part 
    
    return enabledParts  

def get_enabled_feederparts_by_id():
    enabledParts = dict()
    allFeeds = psypnp.search.get_sorted_feeders_list()
    for aFeed in allFeeds:
        if not aFeed.isEnabled():
            continue 
        
        fPart = aFeed.getPart()
        if fPart is None:
            continue 
        
        enabledParts[fPart.getId()] = fPart 
        
    return enabledParts

main()

