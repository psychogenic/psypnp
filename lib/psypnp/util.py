'''
psypnp.util -- various utilities.

The most useful being 
  should_proceed_with_motion()
which should always be checked before moving the 
machine in scripts.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''

from psypnp.ui import (showMessage, getOption)

import psypnp.globals



def machine_is_running():
    if psypnp.globals.machine().isEnabled():
        return True
    showMessage("Hm, is machine started?")
    return False

def should_proceed_with_motion():
    if not machine_is_running():
        return False
    if psypnp.globals.machine().isHomed():
        return True
    
    options = ['Abort', 'Go Anyway']
    val = getOption("Not Homed Yet",
                    "Not homed!  What should we do?",
                    options, 
                    options[0])
    if val == 1:
        return True
    
    return False

def get_bottom_vision():
    partsAl = psypnp.globals.machine().getPartAlignments() # RefBotVision()
    if partsAl is None or not len(partsAl):
        # no bottom vision?
        return None
    botVis = partsAl[0]
    return botVis 


def clone_alignment_pipeline(sourcePart, targets):
    botVis = get_bottom_vision()
    if botVis is None:
        # todo: barf with error?
        return 
    
    sourcePartSettings = botVis.getPartSettings(sourcePart)
    sourcePartPipeline = sourcePartSettings.getPipeline()

    for apart in targets:
        if apart.getId() !=  sourcePart.getId():
            targSettings = botVis.getPartSettings(apart)
            if targSettings is not None:
                print("Setting pipeline for part %s" % apart.getId())
                pipeClone = sourcePartPipeline.clone()
                targSettings.setEnabled(True)
                # print("Setting part settings for %s to %s" % (str(targSettings), str(pipeClone)))
                targSettings.setPipeline(pipeClone)




