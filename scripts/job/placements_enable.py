'''

Play with the board placements enable checkbox, en masse.

Allows you to:
  - Enable (ALL)
  - Disable (ALL)
  - Disable List (comma-sep list, e.g. "R12,J11,J6,J7,J8,J9,J10,JP1,JP4")
  - Disable "un-fed" (all placements that do NOT have a feed associated)
  - Toggle (Invert the current settings)
  
Select a board from the project before running.  
Selecting "Disable List" will provide you with a valid list of what's 
currently disabled.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/


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

def refresh_checkboxen():
    gui.jobTab.getJobPlacementsPanel().repaint()

def get_selected_boards():
    boardsList = psypnp.ui.getSelectedBoards()
    if boardsList is None or not len(boardsList):
        psypnp.ui.showError("Select at least one board")
        return None
    return boardsList


def use_disable_list():
    curDisabledList = []
    boards = get_selected_boards()
    if boards is None:
        return
    placementsHash = {}
    for aboard in boards:
        for aplacement in aboard.getPlacements():
            pid = aplacement.getId()
            placementsHash[pid] = aplacement
            if not aplacement.isEnabled():
                curDisabledList.append(pid)
    itemsToDisable = psypnp.ui.getUserInput('List of items to disable', ','.join(curDisabledList))
    if itemsToDisable is None or not len(itemsToDisable):
        return

    itemsToDisable = re.sub(r"\s+", '', itemsToDisable)
    idList = itemsToDisable.split(',')
    notFoundList = []
    numDisabled = 0
    for anId in idList:
        if anId in placementsHash:
            if placementsHash[anId].enabled:
                placementsHash[anId].enabled = False
                numDisabled += 1
                print("Disabled %s" % anId)
            else:
                print("%s already disabled")
        else:
            notFoundList.append(anId)
    refresh_checkboxen()

    errStr = ''
    if len(notFoundList):
        errStr = '  Not Found: %s' % (','.join(notFoundList))
    psypnp.ui.showMessage("Disabled %i %s" % (numDisabled, errStr))
    return







def set_placements(forboard, toValue):
    numChanged = 0
    for aplacement in forboard.getPlacements():
        if aplacement.isEnabled() != toValue:
            numChanged += 1
            aplacement.setEnabled(toValue)
    return numChanged

def toggle_placements(forboard):
    numChanged = 0
    for aplacement in forboard.getPlacements():
        numChanged += 1
        aplacement.setEnabled(not aplacement.isEnabled())
    return numChanged

def enable_placements(forboard):
    return set_placements(forboard, True)

def disable_placements(forboard):
    return set_placements(forboard, False)

def disable_placements_without_feed(forboard):
    numChanged = 0
    for aplacement in forboard.getPlacements():
        if not aplacement.isEnabled():
            continue
        
        if aplacement.getType() == PlacementType.Fiducial: 
            continue
        
        prt = aplacement.getPart()
        doDisable = False
        if prt is None:
            doDisable = True
        else:
            feeds = psypnp.search.feeds_by_part(prt, onlyEnabled=True)
            if feeds is None:
                doDisable = True
        
        if doDisable:
            numChanged += 1
            aplacement.setEnabled(False)
            
    return numChanged

def act_on_all(using_cb):
    #job = gui.jobTab.getJob()
    #boardLocs = job.getBoardLocations()
    #if not len(boardLocs):
    #    return
    boards = get_selected_boards()
    if boards is None:
        return

    numAffected = 0
    for aboard in boards:
        if True: # bloc.isEnabled():
            numAffected += 1
            #numChanged = set_placements(bloc.board, True)
            numChanged = using_cb(aboard)
            print("Changed enable for %i placements" %  numChanged)
    print("Set placements for %i boards" % numAffected)



def toggle_all():
    job = gui.jobTab.getJob()
    #boardLocs = job.getBoardLocations()
    #if not len(boardLocs):
    #    return
    boards = get_selected_boards()
    if not boards or (not len(boards)) or not boards[0]:
        return
    
    numAffected = 0
    for aboard in boards:
        if True: # bloc.isEnabled():
            numAffected += 1
            #numChanged = set_placements(bloc.board, True)
            numChanged = toggle_placements(aboard)
            print("Changed enable for %i placements" %  numChanged)
    print("Set placements for %i boards" % numAffected)

def select_action_and_perform():

    val = psypnp.ui.getOption("Enable/Disable", 
                "Change component placement 'enable' to",
                ['Toggle', 'Disable Unfed', 'Disable List', 'Disable', 'Enable'])



    if val == 4:
        act_on_all(enable_placements)
    elif val == 3:
        act_on_all(disable_placements)
    elif val == 2:
        use_disable_list()
    if val == 1:
        act_on_all(disable_placements_without_feed)
    elif val == 0:
        act_on_all(toggle_placements)
    else:
        return False

    return True


if select_action_and_perform():
    refresh_checkboxen()


