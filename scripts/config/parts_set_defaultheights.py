'''

Configure the height of a parts with no height set (i.e. 0 height,
like after import creation) based on values in DefaultHeightsMap.

Setup DefaultHeightsMap to your liking.  Keys will be matched to part id.

"0402" will match R_0402, C_0402 etc, whereas "R_0805" won't match caps 
C_0805... you get the picture.

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


import psypnp.debug
from org.openpnp.model import Length
#Length(22, LengthUnit.Millimeters)
from org.openpnp.model import LengthUnit 

import psypnp
import psypnp.ui

HeightUnits = LengthUnit.Millimeters
DefaultHeightsMap = {
    '0402':0.350,
    '0603':0.450,
    'R_0805':0.450,
    'C_0805':0.550,
    'R_1206':0.550,
    'C_1206':0.650,
    'R_1210':0.550,
    'C_1210':0.850,
    'R_1812':0.550
}


SELECTION_ALLMATCHING=2
SELECTION_0HEIGHT = 1

def main():
    selopt = get_user_selection()
    if not selopt:
        return 

    if selopt == SELECTION_ALLMATCHING:
        set_part_heights(True)
    elif selopt == SELECTION_0HEIGHT:
        set_part_heights(False)
    


def get_user_selection():
    selopt = psypnp.ui.getOption("Set default heights", 
                        "Set part heights to default for"
                        , ['Cancel', 
                           '0-height parts', 
                           'All matching parts'])
    
    return selopt
    
    

def set_part_heights(setAll):
    psypnp.debug.out.buffer('Setting parts heights to defaults...')
    
    allParts = config.getParts()
    noHeightParts = []
    for aPart in allParts:
        hValue = aPart.getHeight().getValue()
        if setAll or hValue < 0.001:
            psypnp.debug.out.buffer('No height set for %s' % str(aPart))
            noHeightParts.append(aPart)
            
            
    
    numChanged = 0
    for confedHeight in DefaultHeightsMap.items():
        pheightLen = None # reset this
        for noHPart in noHeightParts:
            pid = noHPart.getId()
            if pid is not None and pid.find(confedHeight[0]) >= 0:
                if pheightLen is None:
                    pheightLen = Length(confedHeight[1], HeightUnits)
                
                psypnp.debug.out.buffer('Setting height to %s for %s' % 
                                        (str(confedHeight[1]), str(aPart)))
                noHPart.setHeight(pheightLen)
                numChanged += 1
    
  
    statusMsg = "Number parts affected: %i" % numChanged
    psypnp.debug.out.flush(statusMsg)
    gui.getPartsTab().repaint()
    psypnp.showMessage(statusMsg)



main()

