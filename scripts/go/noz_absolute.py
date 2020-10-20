'''

Move the nozzle to these (absolute) coordinates.

Will only move things if 
  psypnp.should_proceed_with_motion
says we're good to go.

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



#from __future__ import absolute_import, division

from org.openpnp.model import LengthUnit, Location

import psypnp 
import psypnp.ui




def main():
    if psypnp.should_proceed_with_motion():
        go_cam()



def go_cam():
    loc = get_coords()
    if loc is None:
        # cancel
        return
    machine.defaultHead.moveToSafeZ()
    machine.defaultHead.defaultNozzle.moveTo(loc)


def get_coords():
    noz = machine.defaultHead.defaultNozzle
    curloc = noz.location
    xval = psypnp.ui.getUserInputFloat("X", curloc.x)
    if xval is None:
        # cancel
        return None
    yval = psypnp.ui.getUserInputFloat("Y", curloc.y)
    if yval is None:
        # cancel
        return None

    location = Location(LengthUnit.Millimeters, xval, yval, 0, 0);
    return location

main()
