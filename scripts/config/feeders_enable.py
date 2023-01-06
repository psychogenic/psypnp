'''
Feeders enable/disable.
Options:
  - disable all
  - enable all*
  
Disable will simply do that.  Enable will ask for a part name to ignore.
I use this by setting unused feeders to the "FIDUCIAL-HOME" part so, 
by specifying this string, all feeders _not_ associated with this 
placeholder will be enabled.

For the string, you can use a substring, e.g. 0402, and this will ignore
all *0402* named parts when enabling. Dunno if that's of great use, but 
it's there.
  
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
import psypnp.ui
import psypnp.search
import psypnp.nv 

EnableExceptionPartNameDefault = 'FIDUCIAL-HOME'

def main():
    allFeeds = psypnp.search.get_sorted_feeders_list()
    
    ignoredPartIdsMap = dict() 
    
    
    
    sel = psypnp.ui.getOption('Enable/Disable Feeds', 
                              'Operation to perform on all feeders',
                              ['Enable', 'Disable', 'Cancel'], 'Cancel')
    
    if sel is None or sel < 0 or sel == 2:
        return 
    
    doEnable = False
    if sel == 0:
        ignoredPartIdsMap = get_parts_to_ignore()
        if ignoredPartIdsMap is None:
            return 
        doEnable = True 
        
    
    numAffected = 0
    for aFeed in allFeeds:
        if not doEnable:
            if aFeed.isEnabled():
                aFeed.setEnabled(False)
                numAffected += 1
            continue 
        
        # we're enabling 
        fPart = aFeed.getPart()
        if fPart is None or fPart.getId() in ignoredPartIdsMap:
            # no part associated or this is a part we don't want
            if aFeed.isEnabled():
                aFeed.setEnabled(False)
                numAffected += 1
                
            continue
        
        # part associated and _not_ a part we're ignoring
        if not aFeed.isEnabled():
            numAffected += 1
            aFeed.setEnabled(True)
            
            
    if not numAffected:
        psypnp.ui.showMessage('No feeders affected')
        return 
    
    statuschange = 'disabled'
    if doEnable:
        statuschange = 'enabled'
        
    psypnp.ui.showMessage('%i Feeders %s' % (numAffected, statuschange))
    return 



def get_parts_to_ignore():
    retMap = dict()
    
    mystore = psypnp.nv.NVStorage('fdrsenable')
    ignoredPartNameDefault = mystore.ignoredpart 
    if ignoredPartNameDefault is None:
        ignoredPartNameDefault = EnableExceptionPartNameDefault 
        
    pname = psypnp.ui.getUserInput("Part name (or substr) for feeders to leave disabled", ignoredPartNameDefault)
    
    if pname is None or not len(pname):
        return None 
    
    
    mystore.ignoredpart = pname 
    
    matchingParts = psypnp.search.parts_by_name(pname)
    if matchingParts is None or not len(matchingParts):
        return retMap
        
    for p in matchingParts:
        #print("MATCHED PART %s" % str(p.getId()))
        retMap[p.getId()] = p 
        
    return retMap

main()
