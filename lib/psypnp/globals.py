'''
Created on Oct 15, 2020

globals... this is a way for modules to access the "global"
machine/config/scripting/gui objects.

Adding:

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

to scripts (things available in the OpenPnP Scripts menu) makes it 
so you can 

 import psypnp...

and use the modules without problems or passing around references to these
objects.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''
import os.path

try:
    import javax.swing.JOptionPane as optPane
except:
    from psypnp.debug import stubOptPane as optPane 


_gConfig = None
_gMachine = None
_gScripting = None
_gGUI = None 
_parentDir = None 
def setup(machine, config, scripting, gui):
    global _gConfig, _gMachine, _gScripting, _gGUI, _parentDir
    _gMachine = machine 
    _gConfig = config 
    _gScripting = scripting
    _gGUI = gui 
    
    _parentDir =  os.path.join(scripting.getScriptsDirectory().toString(), '..')
    
def doSetupError():
    optPane.showMessageDialog(None,"psypnp.globals.setup() never called")
    return None 


def fullpathFromRelative(relpath):
    if _parentDir is None:
        return relpath 
    
    return os.path.join(_parentDir, relpath)
    


def basedir():
    global _parentDir
    return _parentDir

def config(): 
    global _gConfig
    if _gConfig is None:
        return doSetupError()
    return _gConfig


def machine(): 
    global _gMachine
    if _gMachine is None:
        return doSetupError()
    return _gMachine


def scripting(): 
    global _gScripting
    if _gScripting is None:
        return doSetupError()
    return _gScripting


def gui(): 
    global _gGUI
    if _gGUI is None:
        return doSetupError()
    return _gGUI

