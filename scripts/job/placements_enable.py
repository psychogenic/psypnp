'''

Play with the board placements enable checkbox, en masse.

Allows you to:
  - Enable (ALL)
  - Disable (ALL)
  - Disable List (comma-sep list, e.g. "R12,J11,J6,J7,J8,J9,J10,JP1,JP4")
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



def refresh_checkboxen():
    gui.jobTab.getJobPlacementsPanel().repaint()

def get_selected_boards():
    boardLocs = gui.jobTab.getSelections()
    if not boardLocs or (not len(boardLocs)) or not boardLocs[0]:
        psypnp.showError("Select at least one board")
        return None
    boardsList = []
    for bloc in boardLocs:
        boardsList.append(bloc.board)

    return boardsList


def use_disable_list():
    curDisabledList = []
    boards = get_selected_boards()
    if boards is None:
        return
    placementsHash = {}
    for aboard in boards:
        for aplacement in aboard.placements:
            pid = aplacement.getId()
            placementsHash[pid] = aplacement
            if not aplacement.enabled:
                curDisabledList.append(pid)
    itemsToDisable = psypnp.getUserInput('List of items to disable', ','.join(curDisabledList))
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
        errStr = '  Not Found: %s' % (','.notFoundList)
    psypnp.showMessage("Disabled %i %s" % (numDisabled, errStr))
    return







def set_placements(forboard, toValue):
    numChanged = 0
    for aplacement in forboard.placements:
        if aplacement.enabled != toValue:
            numChanged += 1
            aplacement.enabled = toValue
    return numChanged

def toggle_placements(forboard):
    numChanged = 0
    for aplacement in forboard.placements:
        numChanged += 1
        aplacement.enabled = not aplacement.enabled
    return numChanged

def enable_placements(forboard):
    return set_placements(forboard, True)

def disable_placements(forboard):
    return set_placements(forboard, False)

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

    val = psypnp.getOption("Enable/Disable", 
                "Change component placement 'enable' to",
                ['Toggle', 'Disable List', 'Disable', 'Enable'])



    if val == 3:
        act_on_all(enable_placements)
    elif val == 2:
        act_on_all(disable_placements)
    elif val == 1:
        use_disable_list()
    elif val == 0:
        act_on_all(toggle_placements)
    else:
        return False

    return True


if select_action_and_perform():
    refresh_checkboxen()


