'''
OpenPnP REPL shell wrapper

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.


The REPL ("Read, Evaluate, Print, Loop") terminal I use to 
muck about within the openpnp python engine.

Launch this, and it will _freeze_ openpnp so you can play 
within the python and use the machine/config/gui/scripting objects
directly.

NOTE: this means that you have to launch openpnp from a terminal
to have some way to interact (and EXIT!! ctrl-d works for me) the
REPL.

To avoid just getting stuck, by default the code asks for a confirmation
before proceeding.  This can be super annoying while coding, so just
disable it with 
  
  
  
  
  
  
below.

NOTE2: AutoHideGUI is useful if you want to auto-switch back to
terminal when running REPL

NOTE3: not using standard boilerplate here because you may often
want to add directories to python path (see extendSysPath() below)
    
'''

# Make certain user knows what's up before launching:
RequestConfirmationOnEveryLaunch = False

# Auto-hide the GUI while terminal is running
# (useful for fast task switching)
AutoHideGUI = False



import os.path
import sys
import code
import logging
import threading

logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)



# add any extra path dirs you want access to here
# just plop directories in the add_dirs_to_sys list
# to be able to import from there
def extendSysPath():
    add_dirs_to_sys = [
        os.path.join(scripting.getScriptsDirectory().toString(), '..', 'lib'),
        scripting.getScriptsDirectory().toString()   
    ]
    
    for adir in add_dirs_to_sys:
        if adir is not None and len(adir) and os.path.exists(adir):
            sys.path.append(adir)


# must do this now to import psypnp utils
extendSysPath()


import psypnp
import psypnp.ui 
import psypnp.globals
import psypnp.repl

# give any modules called access to OpenPnP globals
# (they can use eg psypnp.globals.machine() after this)
psypnp.globals.setup(machine, config, scripting, gui)




# # My stubs stuff... useful for devel in IDE with autocomplete etc
# # you may completely ignore this...
# try:
#     import psypnp_dev.stub_instances
#     if psypnp_dev.stub_instances.HaveStubs:
#         from psypnp_dev.stub_instances import (
#             machine,
#             config,
#             scripting
#             )
#     else:
#        psypnp.globals.setup(machine, config, scripting, gui)
#      
# except:
#     psypnp.globals.setup(machine, config, scripting, gui)
# 
#     



def runInterpreter(extraVars=None):
    '''
        runInterpreter
        This just calls 
          psypnp.repl.runInterpreter
        but is a good place to setup whatever 
        you are working on and save some typing
        by sticking stuff into the variables dictionary.
        
        By default, there are the openpnp globals and a few 
        utility functions available (try "show(o)" for example)
        
    '''
    ### variables in REPL ENV
    # variables will hold all the normal globals
    # and you may add your own for easy access during dev
    variables = globals() 
    
    # e.g. 
    #   import some.module.thing
    #   mything = some.module.thing.Awesome()
    #   variables['awesome'] = mything
    # will give you access to that object straight in the REPL
    # Add stuff to variables here:
    # ...
    
    
    
    
    
    
    ### confirmation requester (unless disabled above
    ### with RequestConfirmationOnEveryLaunch = False)
    if RequestConfirmationOnEveryLaunch:
        launchMsg = "Starting REPL will freeze OpenPnP and you need \naccess to the terminal "
        launchMsg += "it's running from to exit."
        if AutoHideGUI:
            launchMsg += "\nWill hide GUI on launch..."
        launchMsg += " \nProceed?"
        if not psypnp.ui.getConfirmation("Launch REPL?", 
                                         launchMsg):
            # ok, user aborted
            return
    
    
    # by default, we get 
    if extraVars is None:
        extraVars = psypnp.repl.getStandardEnvVars()
    for k in extraVars:
        variables[k] = extraVars[k]
    
    
    if AutoHideGUI:
        gui.hide()
        gui.repaint()
    # actually setup and launch the shell
    psypnp.repl.runInterpreter(variables)
    
    if AutoHideGUI:
        gui.show()
    



# do it! 
# runInterpreter()
runTimeThread = threading.Thread(target = runInterpreter)
runTimeThread.start()

