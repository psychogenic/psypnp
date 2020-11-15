'''

Wrapper for Python REPL shell and utility methods 
to stick in environment.

This is a great way to interact and test OpenPnP scripting.

See/run the zzz_repl script in the Scripts menu.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''

import psypnp.globals
import code 
import os


# try to load readline support and completion
HaveReadlineFullSupport = False
try:
    import atexit
    import readline
    import rlcompleter
    from rlcompleter import Completer
except ImportError:
    print("Module readline not available.")
    
else:
    HaveReadlineFullSupport = True
    readline.parse_and_bind("tab: complete")
    print("AutoCompletion Loaded")

    history_file = os.path.join(os.path.expanduser("~"), ".pyhistory")

    def save_history(history=history_file):
        import readline
        readline.write_history_file(history)


    def load_history(history=history_file):
        try:
            readline.read_history_file(history)
        except IOError:
            pass

    load_history()
    atexit.register(save_history)

    del readline, rlcompleter, atexit, history_file



def runInterpreter(env_vars):
    #variables = globals()
    #print("ENV VARS %s " % str(env_vars))
    #for k,v in env_vars:
    #    variables[k] = v 
    shell = code.InteractiveConsole(env_vars)
    if HaveReadlineFullSupport:
        # this stuff only works on command line, but is helpful
        shell.runcode("import readline\nfrom rlcompleter import Completer\nreadline.parse_and_bind(\"tab: complete\")")
        shell.runcode("readline.set_completer(Completer(locals()).complete)")
        
    shell.interact("Running within OpenPnP. \nUse dir() to get a list of availables...\n\n")



class InterpreterHelper:
        
    def __init__(self):
        pass 
    
    def show(self, v=None, filterMe=None):
        if v is None:
            print("show(VARIABLE [, filter])\nShows nice dir() of VARIABLE\n")
            self.dumpGlobals()
            return
        
        
        filt = None 
        if filterMe is not None:
            filt = filterMe.lower()
            
        ''.startswith('get')
        attr_misc = []
        attr_bool = []
        attr_get = []
        attr_set = []
        for anAttrib in dir(v):
            if anAttrib and len(anAttrib) and anAttrib.find('__') < 0:
                if filt is None or anAttrib.lower().find(filt) >= 0:
                    if anAttrib.startswith('is'):
                        attr_bool.append(anAttrib)
                    elif anAttrib.startswith('get'):
                        attr_get.append(anAttrib)
                    elif anAttrib.startswith('set'):
                        attr_set.append(anAttrib)
                    else:
                        attr_misc.append(anAttrib)
                        
        
        outStr = "\n" + str(v) + "\n"
        
        allAttrs = sorted(attr_bool) + sorted(attr_get) + sorted(attr_set) + sorted(attr_misc)
        for anAttrib in allAttrs:
            outStr += '\t%s\n' % anAttrib
            
        
        print(outStr)
        
    def dumpGlobals(self):
        for k in globals():
            print("G: %s" % str(k))
    
    def listFeeds(self, matchName=None):
        feedIds = []
        for f in psypnp.globals.machine().getFeeders():
            fname = f.getName()
            if matchName is None or fname.find(matchName) > -1:
                feedIds.append(fname)
        
        return sorted(feedIds)
        
            
    def getFeed(self, fname):
        allFeeders = psypnp.globals.machine().getFeeders()
        for f in allFeeders:
            if f.getName() == fname:
                return f
        
        print("No exact match, trying for partials")
        partialMatches = []
        for f in allFeeders:
            n = f.getName()
            if n.find(fname) > -1:
                partialMatches.append(f)
        
        if len(partialMatches):
            return partialMatches
        
        
                
        return None
        
    def listParts(self, matchName=None):
        partIds = []
        for p in psypnp.globals.config().getParts():
            pid = p.getId()
            if matchName is None or pid.find(matchName) > -1:
                partIds.append(pid)
            
        return sorted(partIds)
        
    def getPart(self, pId):
        allParts = psypnp.globals.config().getParts()
        for p in allParts:
            if p.getId() == pId:
                return p
        
        # not found... 
        print("No exact match, trying for partials")
        partialMatches = []
        for p in allParts:
            pid = p.getId()
            if pid.find(pId) > -1:
                partialMatches.append(p)
        
        if len(partialMatches):
            return partialMatches
        return None
    
    def listPackages(self, matchName=None):
        packageIds = []
        for p in psypnp.globals.config().getPackages():
            pid = p.getId()
            if matchName is None or pid.find(matchName) > -1:
                packageIds.append(pid)
        return sorted(packageIds)
    
    def getPackage(self, pId):
        allPackages = psypnp.globals.config().getPackages()
        for p in allPackages:
            if p.getId() == pId:
                return p
        
        # not found... 
        print("No exact match, trying for partials")
        partialMatches = []
        for p in allPackages:
            pid = p.getId()
            if pid.find(pId) > -1:
                partialMatches.append(p)
        
        if len(partialMatches):
            return partialMatches
        return None

def getStandardEnvVars():
    variables = dict()
    
    interpHelper = InterpreterHelper()
    
    #a=interpHelper.listFeeds
    defaultsV = dict()
    defaultsV['o'] =interpHelper
    defaultsV['show'] = interpHelper.show

    for k in defaultsV:
        variables[k] = defaultsV[k]
    return variables




