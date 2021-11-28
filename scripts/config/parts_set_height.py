'''

Configure the height of a batch of parts, based on substring of
part id.

With this, you can set all the, e.g. 0402s to 0.1mm in one go.

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


from org.openpnp.model import Length
#Length(22, LengthUnit.Millimeters)
from org.openpnp.model import LengthUnit 

import psypnp
import psypnp.ui


def main():
    set_part_heights()

def get_height_len():
    lenstr = psypnp.ui.getUserInputFloat("Enter desired height (mm)", 1.234)
    try:
        heightval = float(lenstr)
        height = Length(heightval, LengthUnit.Millimeters)
    except:
        height = Length.parse(lenstr)

    return height

def set_part_heights():
    keepGoing = True
    while keepGoing:
        pname = psypnp.getUserInput("Name of part, or substring thereof", "C_0603")
        if pname is None or not len(pname):
            return
        height = get_height_len()
        if height is None:
            return
    
        numChanged = 0
        for apart in config.getParts():
            if pname == '*' or apart.id.find(pname) >= 0:
                numChanged += 1
                apart.setHeight(height)
    
        statusMsg = "Number parts affected: %i" % numChanged
        print(statusMsg)
        gui.getPartsTab().repaint()
        psypnp.showMessage(statusMsg)



main()