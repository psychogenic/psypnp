'''
Automated method to reset the part association for all feeders.
Since we can use scripts to configure the feeds, this is mainly a utility 
to simplify 'clean-up' and isn't really required.

What it does: asks for confirmation that you want to proceed, requests
a part to associate to all feeds (defaults to the homing fiducial) and then
does the association while disabling the feed.

@note: you must have at least one part configured to associate to these.

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


def main():
    if not feeders_reset_proceed():
        return 
    
    allFeeds = psypnp.search.get_sorted_feeders_list()
    
    selPart = get_part_to_use()
    if selPart is None:
        return 
    
    for aFeed in allFeeds:
        aFeed.setPart(selPart)
        aFeed.setEnabled(False) 
    
        
    
def feeders_reset_proceed():
    
    return psypnp.ui.getConfirmation("Feeders Reset", 
                              "This will reset all feeder part associations.\nProceed?",
                              optDefault='No')

def get_part_to_use():
    
    
    matchingParts = []
    while len(matchingParts) != 1:
        pname = psypnp.ui.getUserInput("Part to associate to all feeders", 'FIDUCIAL-HOME')
        if pname is None or not len(pname):
            return None 
        
        
        matchingParts = psypnp.search.parts_by_name(pname)
        if matchingParts is None or not len(matchingParts):
            psypnp.ui.showError("No parts found for '%s'" % pname)
        elif len(matchingParts) > 1:
            psypnp.ui.showError("%i parts match '%s'.\nNeed more specifics..." % (len(matchingParts), pname))
        
    return matchingParts[0]

main()
