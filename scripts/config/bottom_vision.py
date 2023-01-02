'''

Manage bottom vision status (enable/disable/toggle)

This is useful under a few circumstances, but I wrote it mainly for the
case when a bunch of new parts are created during a board import and they
all have to be hunted down to disable so-so bottom vision operation.

This is why parts may be selected by height (defaults to 0.0 on creation),
as well as by part or package name.


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
import psypnp.search 
import psypnp.ui 
import psypnp.util
import psypnp.nv

# this needs to match getSelection() order
SEL_BYNAME = 0
SEL_BYPACKAGE = 1
SEL_BYHEIGHT = 2
SEL_ALL = 3

# this needs to match getOperation() order
OP_ENABLE = 0
OP_DISABLE = 1
OP_TOGGLE = 2

class PartFetcher:
    '''
        Part fetcher -- little utility class 
        to query user and get matching parts.
        Its job is just to return a [list] of parts and 
        keep track of whether user aborted.
    '''
    def __init__(self):
        self.aborted = False  
        # non-volatile storage, to recall last entered data
        self.nvSettings = psypnp.nv.NVStorage('botvizstat')
    
    def wasAborted(self):
        return self.aborted 
    
    
    def byName(self):
        
        # get default from NV storage
        defValue = self.nvSettings.byname 
        if defValue is None:
            defValue = 'C_0603'
        
        pname = psypnp.ui.getUserInput("Name of part, or substring thereof", 
                                       defValue)
        if pname is None or not len(pname):
            self.aborted = True 
            return []
        
        # remember this as default for next time
        self.nvSettings.byname = pname 
        
        return psypnp.search.parts_by_name(pname)
    
    def allParts(self):
        return psypnp.globals.config().getParts()

    def byPackage(self):
        
        # get default from NV storage
        defValue = self.nvSettings.bypkg 
        if defValue is None:
            defValue = 'R0402'
        pname = psypnp.ui.getUserInput("Name of package, or substring thereof", 
                                       defValue)
        if pname is None or not len(pname):
            self.aborted = True 
            return []
        
        # remember this as default for next time
        self.nvSettings.bypkg = pname 
        
        return psypnp.search.parts_by_package_name(pname)
    
    def byHeight(self):
        pheight = psypnp.ui.getUserInputFloat("Height of package", 
                                              0.0)
        if pheight is None:
            self.aborted = True 
            return []
        
        matchingParts = []
        for apart in psypnp.globals.config().getParts():
            h = apart.getHeight()
            if h is not None and h.getValue() == pheight:
                matchingParts.append(apart)
                
        return matchingParts
    
        

def main():
    
    partSrc = PartFetcher()
    
    fetcherMap = {
        SEL_BYNAME: partSrc.byName,
        SEL_BYPACKAGE: partSrc.byPackage,
        SEL_BYHEIGHT: partSrc.byHeight,
        SEL_ALL: partSrc.allParts
    }
    
    sel = getSelection()
    while sel is not None:
        if sel not in fetcherMap:
            # this is weird.
            print("AAgh! selection not in fetcher map??")
            return 
        
        parts = fetcherMap[sel]() 
        if partSrc.wasAborted():
            return 
        
        if parts is None or not len(parts):
            psypnp.ui.showError("Could not find any matching parts...")
            continue
        
        op = getOperation(len(parts))
        if op is None:
            return
        
        setVisionTo = False 
        
        if op == OP_ENABLE:
            setVisionTo = True 
            print("Enabling bottom vision")
        elif op == OP_TOGGLE:
            setVisionTo = None 
            print("Toggling bottom vision")
        elif op == OP_DISABLE:
            setVisionTo = False 
            print("Disabling bottom vision")
        else:
            psypnp.ui.showError("Something wroooong")
            return 
            
            
        if not setBottomVisionTo(parts, setVisionTo):
            # didn't work out.
            return 
        
        tab = psypnp.globals.gui().getPartsTab()
        if tab is not None:
            # this doesn't really do what I want (refresh
            # the damn children) but this API is crap. TODO:FIXME
            tab.repaint()
            
        
            
        # ask for more work
        sel = getSelection()
        

def getSelection():
    sel =  psypnp.ui.getOption("Bottom Vision", 
                "Enable/disable bottom vision for part(s)",
                ['By Name', 'By Package', 'By Height', 'All', 'Cancel'], 'Cancel')
    
    if sel == 4 or sel < 0:
        # cancel
        return None 
    
    return sel

def getOperation(numParts):
    
    pluralParts = 's'
    if numParts == 1:
        pluralParts = ''
    operation =  psypnp.ui.getOption("Operation", 
                "Set bottom vision for %i part%s" % (numParts, pluralParts),
                ['Enable', 'Disable', 'Toggle', 'Cancel'], 'Toggle')
    
    if operation == 3 or operation < 0:
        return None 
    
    return operation

def setBottomVisionTo(forPartsList, setTo=None):
    '''
        setBottomVisionTo(PLIST, [SETTO])
        Set bottom vision enabled/disabled for 
        each part in part list PLIST, according to
        SETTO.
        If SETTO is None, will toggle.
    '''
    botVis = psypnp.util.get_bottom_vision()
    if botVis is None:
        psypnp.ui.showError("No bottom vision??")
        return False
     
    psetting = False
    for apart in forPartsList:
        targSettings = botVis.getPartSettings(apart)
        if targSettings is not None:
            if setTo is not None:
                psetting = setTo 
            else: 
                psetting = not targSettings.isEnabled()
            
            try:
                print("Set bot vis for %s to %s" % (str(apart.getId()), str(psetting)))
            except:
                pass
            
            targSettings.setEnabled(psetting)
            
    return True
    
        
main()
