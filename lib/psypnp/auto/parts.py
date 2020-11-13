'''
Created on Oct 16, 2020

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

# useful for devel in IDE with autocomplete etc
try:
    import psypnp_dev.stub_instances
    if psypnp_dev.stub_instances.HaveStubs:
        from psypnp_dev.stub_instances import (
            machine,
            config,
            scripting
            )
except:
    pass

import psypnp.csv_file
import psypnp.globals
import psypnp.debug

#BOMParserType=psypnp.csv_file.BOMParserKicad
class ProjectPart:
    
    def __init__(self, bomEntry, pnpPart, package_desc=None):
        self.bom_entry = bomEntry
        self.part = pnpPart
        self.package_description = package_desc
        
    def quantity(self):
        return self.bom_entry.quantity
    
    def getValue(self):
        return self.bom_entry.value 
        
    def getId(self):
        if self.part is not None:
            return self.part.getId()
        return 'N/A PID'
    
    
    def __string__(self):
        return '%s (%s %i/board)' % (self.part.getId(), self.bom_entry.shortReferences(), self.bom_entry.quantity)
    
    def __repr__(self):
        return '<ProjectPart %s>' % self.__string__()
    
    
    

class PartMap:
    
    MinPercentageForSuccess = 49.0
    
    def __init__(self, bom_filename, BOMParserType):
        self.bom_csv = psypnp.csv_file.BOMCSV(bom_filename, BOMParserType)
    
    
        self._parts_map = dict()
        self.parts = []
        self.notfound = []
        self.bom_entry_found_count = 0
        self.bom_entry_notfound_count = 0
        self.bom_entriesprocessed_count = 0
        self.percentage_mapped = 0.0
        
        if not self.bom_csv.parser.success:
            psypnp.ui.showError("Could not parse BOM %s" % bom_filename)
            return
        
        
    
    
    def map(self):
        
        for apart in psypnp.globals.config().getParts():
            self._parts_map[apart.getId()] = apart
        
        success_count = 0
        notfound_count = 0
        for bomEntry in self.bom_csv.entries():
            openpnpName = self.entryOpenPnPName(bomEntry)
            if openpnpName in self._parts_map:
                success_count += 1
                self.parts.append(ProjectPart(bomEntry, self._parts_map[openpnpName]))
            else:
                self.notfound.append(bomEntry)
                notfound_count += 1
                
        
        self.bom_entry_found_count = success_count
        self.bom_entry_notfound_count = notfound_count
        self.bom_entriesprocessed_count = success_count + notfound_count
        
        if success_count or notfound_count:
            self.percentage_mapped = success_count * 100.0/(1.0*(success_count+ notfound_count))
        
        sorted_parts = sorted(self.parts, key=lambda apart: 1.0/apart.quantity())
        self.parts = sorted_parts
            
        return self.percentage_mapped >= PartMap.MinPercentageForSuccess 
    
    
    
    def numMapped(self):
        return self.bom_entry_found_count
    def numSkipped(self):
        return self.bom_entry_notfound_count
    def numInBOM(self):
        return self.bom_entriesprocessed_count
    
    def entryOpenPnPName(self, bomEntry):
        # TODO: kicad naming  specific?
        return '%s-%s' % (bomEntry.package, bomEntry.value)

    