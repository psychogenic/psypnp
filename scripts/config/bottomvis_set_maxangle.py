'''

Set max valid angle for bottom vision.  I don't think this 
actually has an impact/works...

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


def main():
    partsAl = machine.getPartAlignments()
    if partsAl and len(partsAl) and partsAl[0]:
        botvis = partsAl[0]
        val = psypnp.getUserInput("Max Angular Offset", botvis.getMaxAngularOffset())
        if (val is not None):
            try:
                val = float(val)
            except:
                val = botvis.getMaxAngularOffset()
            if val >=0 and val <=45:
                botvis.setMaxAngularOffset(val)
                psypnp.showMessage("Max angle now %s" % str(botvis.getMaxAngularOffset()))
            else:
                psypnp.showError("Need a val between 0-45")
    else:
        psypnp.showError("Don't have bottom vision?")

main()
