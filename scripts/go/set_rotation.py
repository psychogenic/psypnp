'''


Set the nozzle rotation to this value.

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

from org.openpnp.model import LengthUnit, Location
from org.openpnp.util import MovableUtils
import psypnp
import psypnp.ui

HardMaxAngle = 360

def main():
    if psypnp.should_proceed_with_motion():
        submitUiMachineTask(go_angle)


def go_angle():
    nozzle = machine.defaultHead.defaultNozzle
    curloc = nozzle.location
    val = psypnp.ui.getUserInputFloat("Go Rotation", curloc.rotation)
    if val is None:
        #cancel
        return
    if val < (-1 * HardMaxAngle) or val > HardMaxAngle:
        psypnp.ui.showError("Only angles <= abs(%s) supported" % str(HardMaxAngle))
        return 
    
    loc = Location(LengthUnit.Millimeters, curloc.x, curloc.y, curloc.z, val);
    # nozzle.moveTo(loc)
    MovableUtils.moveToLocationAtSafeZ(nozzle, loc)

main()
