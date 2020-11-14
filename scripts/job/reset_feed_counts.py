'''
Resets feeder count to 0, for all|enabled feeders.

Useful when you have just reloaded feeders between jobs of 
the same set of PCBs, for example.

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
import psypnp.nv # non-volatile storage
import psypnp.search


OP_RESET_ALL=0
OP_RESET_ENABLED=1
OP_CANCEL=2

def main():
    sel = main_selection()
    
    if sel is None or sel == OP_CANCEL:
        return 
    
    onlyEnabled = True
    if sel == OP_RESET_ALL:
        onlyEnabled = False 
    
    
    numChanged = reset_feeds(enabledOnly=onlyEnabled)
    if not numChanged:
        psypnp.ui.showMessage("No feeds affected")
        return
    
    if numChanged == 1:
        psypnp.ui.showMessage("One feeder reset")
        return
    
    
    psypnp.ui.showMessage("%i feeders reset" % numChanged)
        
        
def reset_feeds(enabledOnly):
    
    numChanged = 0
    for afeed in psypnp.search.get_sorted_feeders_list():
        if afeed.isEnabled() or not enabledOnly:
            if hasattr(afeed, 'getFeedCount') and afeed.getFeedCount() > 0:
                afeed.setFeedCount(0)
                numChanged += 1
    
    return numChanged 

def main_selection():
    sel =  psypnp.getOption("Reset Count", 
                           "Reset feeder pick count to 0 for ",
                ['All', 'Enabled Feeders', 'Cancel'], 'Enabled Feeders')
    
    if sel < 0:
        return OP_CANCEL
    
    return sel

main()
