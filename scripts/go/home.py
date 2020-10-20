'''

Send the machine home.

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


from psypnp import should_proceed_with_motion



def main():
    if should_proceed_with_motion():
        go_cam()


def go_cam():
    cam = machine.defaultHead.defaultCamera
    location = Location(LengthUnit.Millimeters, 0, 0, 0, 0);
    cam.moveTo(location)

    
main()
