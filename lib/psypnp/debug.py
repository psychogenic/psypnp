'''
Created on Oct 15, 2020

Debugging output... buffers output to clean up openpnp traces 
and make things more legible.


  psypnp.debug.out.buffer("A")
  psypnp.debug.out.buffer("B")
  psypnp.debug.out.buffer("C")
  
and then
  psypnp.debug.out.flush("D") 
or
  psypnp.debug.out.flush() 
  
@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''


class DebugOptPane:
    def __init__(self):
        pass
    def showMessageDialog(self, whatevs, msg):
        print(str(msg))
    
    
    
stubOptPane = DebugOptPane()

class DebugOut:
    '''
        DebugOut, available through
        psypnp.debug.out
        instance.  
        
        Useful to globally enable/disable debug and to 
        reduce noise on output, by buffering
        debug output prior to flushing, so rather than get:      
                                                        
          2020-10-17 10:55:20.725 SystemLogger INFO: >>> Doing whatever ...                                                              
          2020-10-17 10:55:30.045 SystemLogger INFO: >>> >>> step 1   
          2020-10-17 10:56:53.662 SystemLogger INFO: >>> >>> step 2
          2020-10-17 10:56:53.662 SystemLogger INFO: >>> >>> some info
          2020-10-17 10:56:53.662 SystemLogger INFO: >>> last step done.
          
        You can 
            psypnp.debug.out.buffer("Doing whatever ...")
            # keep buffering stuff and finally
            psypnp.debug.out.flush("last step done.")
        and get the more legible:
                
          2020-10-17 10:55:20.725 SystemLogger INFO: >>> 
           Doing whatever ...
           step 1
           step 2
               some info
           last step done.
        
    '''
    
    def __init__(self):
        self.outbuf = ''
        self.enabled = True # disable actual print() calls with this
        self.forceAutoFlush = False # useful when crashing, to output all buffer() immediately
        self.is_verbose = False
        self.crumbs = dict()
        self.maxlinelen = 80
        
    def crumb(self, name):
        if name in self.crumbs:
            self.crumbs[name] += 1
        else:
            self.crumbs[name] = 1
        
        print("%s: %i" % (name, self.crumbs[name]))
        
    def clearCrumb(self, name):
        if name in self.crumbs:
            del self.crumbs[name]
            
    def clearAllCrumbs(self):
        self.crumbs = dict()
            
    
    def buffer(self, msg, autoEnter=True):
        
        if autoEnter:
            self.outbuf += str(msg) + "\n"
        else:
            self.outbuf += str(msg)
            
        if self.forceAutoFlush or len(self.outbuf) >= self.maxlinelen:
            self.flush()
            
    def verbose(self, msg, autoEnter=True):
        if self.is_verbose:
            self.buffer(msg, autoEnter)
            
    def flush(self, extrastr=None):
        if extrastr is not None:
            self.buffer(extrastr)
        if self.enabled:
            print(self.outbuf)
        self.outbuf = ''
        
        
            
    
out = DebugOut()
