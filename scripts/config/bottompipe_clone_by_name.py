'''

Clone the bottom vision pipeline from some template part to others, 
selecting the affected parts by name.

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
import psypnp.util

def main():
    clone_part_bottom_pipeline()


def clone_part_bottom_pipeline():
    pname = psypnp.getUserInput("Name of part to clone from, or substring thereof", "C_0603")
    if pname is None or not len(pname):
        return
    numChanged = 0

    matchingParts = psypnp.parts_by_name(pname)
    if not len(matchingParts):
        psypnp.showError("No parts matching name found")
        return

    if len(matchingParts) > 1:
        psypnp.showError("Too many matches--don't know which to choose")
        return

    sourcePart = matchingParts[0]
    sourcePackage = sourcePart.getPackage()

    targname = psypnp.getUserInput("Name of part(s) to clone to, \nor substring thereof", "C_0603")
 
    partsWithThisName = psypnp.parts_by_name(targname)
    if partsWithThisName is None or not len(partsWithThisName):
        psypnp.showError("Don't seem to be many targets with this package around")
        return


    val = psypnp.getOption("Really proceed?", 
           "Copy bottom view pipeline from %s to %i\nparts with name containing '%s'?" %
                (sourcePart.getId(), len(partsWithThisName), targname),
                ['Abort', 'Yes, proceed'])
    if val != 1:
        return

    print("Using part %s as source for bottom vision pipeline" % sourcePart.getId())
    psypnp.util.clone_alignment_pipeline(machine, sourcePart, partsWithThisName)
    print("ALL DONE")
    gui.getPartsTab().repaint()


main()
