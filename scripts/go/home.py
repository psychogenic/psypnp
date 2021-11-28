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
# submitUiMachineTask should be used for all code that interacts
# with the machine. It guarantees that operations happen in the
# correct order, and that the user is presented with a dialog
# if there is an error.
from org.openpnp.util.UiUtils import submitUiMachineTask
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
from org.openpnp.util import MovableUtils
from psypnp import should_proceed_with_motion

def main():
    if should_proceed_with_motion():
        submitUiMachineTask(go_cam)


def go_cam():
    cam = machine.defaultHead.defaultCamera
    location = Location(LengthUnit.Millimeters, 0, 0, 0, 0);
    MovableUtils.moveToLocationAtSafeZ(cam, location)

    
main()
