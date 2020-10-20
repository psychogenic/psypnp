'''

The cross up/down/left/right scripts move the head by 
the amount set in NV storage by this very script (85mm 
by default).

Run this to change the value.

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


import psypnp
import psypnp.config.distances
import psypnp.config.storagekeys as keys

ParentKey = keys.CrossFeedScripts
SubKey = keys.CrossSmallFeedDistance

# LastAttemptedValue -- cache for failed user attempts
LastAttemptedValue = None


def main():
    # keep trying this until user succeeds or quits
    while set_crossfeed_distance():
        pass 
    
    
# set_file_location our main logic
def set_crossfeed_distance():
    global LastAttemptedValue
    
    # first, try and set default input value to 
    # whatever user entered last
    distdefault = LastAttemptedValue
    
    if distdefault is None:
        # nothing there, this is our first run
        # try to get default from db
        distdefault = psypnp.nv.get_subvalue(ParentKey, 
                                             SubKey, 
                                             psypnp.config.distances.SmallFeedDefault)
            
    dist = psypnp.ui.getUserInputFloat(
        "Distance to travel when calling 'crosssmall*' scripts", distdefault)
    if dist is None:
        # aborted/canceled
        return False 
    
    LastAttemptedValue = dist
    if dist < 0.5 or dist > 3000:
        psypnp.ui.showError("Valid distances are >0 and <insanity")
        return True
    
    # got something valid, store that for later use
    psypnp.nv.set_subvalue(ParentKey, SubKey, dist)
    
    psypnp.ui.showMessage("OK, distance now set to %s " % str(dist))
    
    return False 

# run all that
main()
    
