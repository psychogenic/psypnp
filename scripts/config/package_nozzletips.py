'''

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

# OnlySetNozzletipOnPackagesWithoutAny -- safer to leave true
# but you know what yer doin'
OnlySetNozzletipOnPackagesWithoutAny = True


OP_CANCEL=0
OP_LIST_NO_NOZZLE=1
OP_SET_NOZZLETIP=2

def main():
    sel = selected_operation()
    doContinue = True
    while sel != OP_CANCEL and doContinue:
        
        if sel == OP_LIST_NO_NOZZLE:
            doContinue = list_no_nozzletips()
        if sel == OP_SET_NOZZLETIP:
            doContinue = set_nozzletip()
        
        if doContinue:
            sel = selected_operation()
        

def selected_operation():
    
    sel = psypnp.ui.getOption("Package NozzleTips", 
                              "What would you like to do?", 
                              ['Cancel', 'No NozzleTips?', 'Set NozzleTip'], 'Cancel')
    
    if sel is None or sel < 0:
        return OP_CANCEL 
    
    return sel


def noNozzleTipForPackage(apkg):
    return apkg is not None and not len(apkg.getCompatibleNozzleTips())

def list_no_nozzletips():
    packagesList = []
    packageIds = []
    for apkg in psypnp.globals.config().getPackages():
        if noNozzleTipForPackage(apkg):
            packagesList.append(apkg)
            packageIds.append(apkg.getId())
    
    if not len(packagesList):
        psypnp.ui.showMessage("All packages have at least \none nozzle tip associated")
        return True 
    
    
    packageIds = sorted(packageIds)
    
    
    pluralized = 's'
    if len(packageIds) == 1:
        pluralized = ''
        
        
    groupsOThree = [packageIds[3*i:(3*i)+3] for i in range((len(packageIds)/3) +1)]
    if not groupsOThree[-1]:
        groupsOThree = groupsOThree[:-1]
    
    asStrs = []
    for agrp in groupsOThree:
        asStrs.append(', '.join(agrp))
        
    psypnp.ui.showMessage("%i package%s have no noz tips:\n%s" % (
                            len(packageIds),
                            pluralized,
                            '\n'.join(asStrs)))
    
    return True 


def set_nozzletip():
    
    ntcoll = psypnp.globals.machine().getNozzleTips()
    if ntcoll is None or not len(ntcoll):
        psypnp.ui.showError("Eeeks, no nozzletips found?")
        return True 
    ntList = ntcoll.toArray()
    
    optTip = []
    tipsByName = dict()
    for nt in ntList:
        ntName = nt.getName()
        if ntName is None or not len(ntName):
            ntName = nt.getId() 
            
        #print("NT %s" % str(nt))
        tipsByName[ntName] = nt 
        optTip.append(ntName)
        
    optTip = sorted(optTip)
        
    ntidx = psypnp.ui.getOption("Which Tip?", "Select nozzletip to set", 
                                optTip)
    
    if ntidx is None or ntidx < 0:
        # cancelled
        return False
    
    #psypnp.ui.showError("Selected tip %s" % tipsByName[optTip[ntidx]].getName())
    
    pkgList = []
    while not len(pkgList):
        pkgname = psypnp.ui.getUserInput("Which package(s) to apply to?", 'SOT-23-5')
    
        if pkgname is None or not len(pkgname):
            return False
        
        pkgList = []
        if pkgname == '*':
            pkgList = psypnp.globals.config().getPackages()
        else:
            pkgList = psypnp.search.packages_by_name(pkgname)
        
        if not len(pkgList):
            psypnp.ui.showError("No matches for '%s'" % pkgname)
    
    
    if OnlySetNozzletipOnPackagesWithoutAny:
        toSetList = []
        for apkg in pkgList:
            if noNozzleTipForPackage(apkg):
                toSetList.append(apkg)
                
        if not len(toSetList):
            psypnp.ui.showError(
                "All %i packages already have a nozzletip\nand only-set-on-empty is True"
                % len(pkgList))
                
            return True
        
        pkgList = toSetList
        
    
    
    if not psypnp.ui.getConfirmation("Set nozzletip?", 
                                     "Really set tip %s to %i package(s)?"
                                     % (optTip[ntidx], len(pkgList))):
        return True
    
    
    for apkg in pkgList:
        apkg.addCompatibleNozzleTip(tipsByName[optTip[ntidx]])
        
    #packages_by_name
    psypnp.ui.showMessage("Nozzle tip %s set" % (optTip[ntidx]), "Done")
    return True
    
main()
