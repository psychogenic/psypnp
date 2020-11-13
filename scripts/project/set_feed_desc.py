'''
Set the (nv-stored) location for the "feed description" CSV 
file, used by the auto_feed_setup script.

This location can be relative (to the openpnp config directory)
or absolute.
     
    
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


import psypnp
import psypnp.config.storagekeys as keys

ParentKey = keys.ProjectManager
SubKey = keys.FeedDescCSV

# LastAttemptedFileName -- cache for failed user attempts
LastAttemptedFileName = None


def main():
    # keep trying this until user succeeds or quits
    while set_file_location():
        pass 
    
    
# set_file_location our main logic
def set_file_location():
    global LastAttemptedFileName
    
    # first, try and set default input value to 
    # whatever user entered last
    fdefault = LastAttemptedFileName
    
    if fdefault is None:
        # nothing there, this is our first run
        # try to get default from db
        fdefault = psypnp.nv.get_subvalue(ParentKey, SubKey)
        # still no go, hard-coded default
        if fdefault is None:
            fdefault = 'data/feed_desc.csv'
            
            
    flocation = psypnp.ui.getUserInput("Relative location for feed desc CSV", fdefault)
    if flocation is None:
        # aborted/canceled
        return False 
    
    LastAttemptedFileName = flocation
    
    fullpath = psypnp.globals.fullpathFromRelative(flocation)
    
    if not os.path.exists(fullpath):
        psypnp.ui.showError("Can't find %s" % fullpath)
        return True 
    
    # we did find it, store that for later use
    
    psypnp.nv.set_subvalue(ParentKey, SubKey, flocation)
    psypnp.ui.showMessage("OK, feed desc at %s " % flocation)
    return False 

# run all that
main()
    