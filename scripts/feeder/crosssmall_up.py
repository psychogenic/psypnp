'''

Quick script to move across a feeder (or anything, really)

Have:
 up/down/left/right
versions of script.

Distance traveled by these defaults 
to 85mm but can be set in NV storage using the 
 set_crosssmall_distance
script.

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



from org.openpnp.model import LengthUnit, Location


import psypnp
import psypnp.nv
import psypnp.config.distances
import psypnp.config.storagekeys

def main():
    if psypnp.should_proceed_with_motion():
        go_cam()


def go_cam():
    loc = get_coords()
    if loc is None:
        # cancel
        return
    if machine.defaultHead is None or machine.defaultHead.defaultCamera is None:
        return

    machine.defaultHead.moveToSafeZ()
    machine.defaultHead.defaultCamera.moveTo(loc)


def get_coords():
    cam = machine.defaultHead.defaultCamera
    curloc = cam.location
    
    # get the configured "smallfeed" distance, or default
    dist = psypnp.nv.get_subvalue(
        psypnp.config.storagekeys.CrossFeedScripts, 
        psypnp.config.storagekeys.CrossSmallFeedDistance,
        psypnp.config.distances.SmallFeedDefault)
    
    xval = 0 
    yval = dist
    location = curloc.add(Location(LengthUnit.Millimeters, xval, yval, 0, 0))
    return location

main()
