'''
Created on Oct 17, 2020

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''
from psypnp.auto.parts import PartMap
import psypnp.debug 
class Project:
    def __init__(self, bom_filename, BOMParserType, name=None):
        
        
        self.name = bom_filename
        if name is not None: 
            self.name = name 
        
        psypnp.debug.out.buffer("Project creating partmap")
            
        self.part_map = PartMap(bom_filename,BOMParserType)
        psypnp.debug.out.buffer("Partmap created")
        
        self.part_map_ok = self.part_map.map()
        if not self.part_map_ok:
            psypnp.debug.out.flush("Project.PartMap Couldn't map enough parts?")
        
        
    def isOK(self):
        return self.part_map_ok
    
    
    def numMapped(self):
        return self.part_map.numMapped()
    
    def numInBOM(self):
        return self.part_map.numInBOM()
    
    def __string__(self):
        return '%s (found %i/%i parts)' % (self.name, 
                                              self.part_map.numMapped(), 
                                              self.part_map.numInBOM())
    
    def __repr__(self):
        return '<Project %s>' % self.__string__()
    
        
