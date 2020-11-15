'''
Capture current state of feeders to a CSV file such that it may be 
inspected and restored later.


@note: currently only really handles reference strip feeders and have 
       yet to code up the restore version of the script.

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


from org.openpnp.model import Location, Length, LengthUnit 


import csv as csv_module

import psypnp
import psypnp.search 
import psypnp.nv # non-volatile storage

StorageParentName = 'fdrdumps'
IncludeDisabledOfSamePart = False
FeedIdCounter = 0
LocationPrecisionFormat = "{:.4f}"
class FeedEntry:
    def __init__(self, stype, id, name, loc, part, disabled=False):
        global FeedIdCounter
        self.fid = FeedIdCounter
        FeedIdCounter += 1
        self.id = id
        self.type = stype
        self.name = name
        self.location = loc
        self.part = part
        self.disabled = disabled
        
    def _floatToSaneString(self, val):
        if val == 0.00000:
            return '0'
        
        return LocationPrecisionFormat.format(val)
        
    def locationToColumn(self, loc):
        vals = [
            str(loc.getUnits().ordinal()),
            self._floatToSaneString(loc.getX()),
            self._floatToSaneString(loc.getY()),
            self._floatToSaneString(loc.getZ()),
            self._floatToSaneString(loc.getRotation())
        ]
        
        return '|'.join(vals)
        
    def toCSVList(self):
        return [
                self.fid,
                self.type,
                self.id, 
                self.name, 
                self.part.getId(),
                str(not self.disabled),
                self.locationToColumn(self.location)
            
            ]
        
    def CSVColumnNamesList(self):
        return [
                'idx',
                'type',
                'id',
                'name',
                'part',
                'enabled',
                'location'
            ]
    def __str__(self):
        return '%s %s %s %s' % (
            str(self.fid),
            self.type, 
            self.name, 
            str(self.part))
        
    def __repr__(self):
        return '<FeedEntry %s>' % str(self)
        
class StripFeedEntry(FeedEntry):
    def __init__(self, id, name, loc, ref_hole, last_hole, part, disabled=False):
        FeedEntry.__init__(self, 'strip', id, name, loc, part, disabled)
        self.reference_hole = ref_hole
        self.last_hole = last_hole
        
    
    def CSVColumnNamesList(self):
        vals = FeedEntry.CSVColumnNamesList(self)
        vals.append('refhole')
        vals.append('lasthole')
        return vals
        
    def toCSVList(self):
        vals = FeedEntry.toCSVList(self)
        vals.append(self.locationToColumn(self.reference_hole))
        vals.append(self.locationToColumn(self.last_hole))
        return vals


def main():
    
    lastProjName = psypnp.nv.get_subvalue(StorageParentName, 'projname')
    lastFileName = psypnp.nv.get_subvalue(StorageParentName, 'filename')
    if lastProjName is None:
        lastProjName = 'My Project'
        
    if lastFileName is None:
        lastFileName = '/tmp/feeds_config.csv'
        
    feed_info = freeze_feeders()
    if feed_info is None or not len(feed_info):
        psypnp.showMessage("No enabled feeds to map")
        return
        
    projname = psypnp.getUserInput("Name of project", lastProjName)
    if projname is None:
       return
    fname = psypnp.getUserInput("Save as CSV file", lastFileName)
    if fname is None:
        return
        
    psypnp.nv.set_subvalue(StorageParentName, 'projname', projname, False)
    psypnp.nv.set_subvalue(StorageParentName, 'filename', fname)
    numFeeds = generate_backup(feed_info, projname, fname)
    psypnp.showMessage("Saved %i feeds to %s" % (numFeeds, fname))

def process_feed_tray(aFeed):
    pass
    
def process_feed_strip(aFeed):
    name = aFeed.getName()
    if name is None or not len(name):
        name = aFeed.getId()
        
    return StripFeedEntry(aFeed.getId(), name, 
                             aFeed.getLocation(), 
    	                     aFeed.getReferenceHoleLocation(), 
                             aFeed.getLastHoleLocation(),
                             aFeed.getPart(), 
    	not aFeed.isEnabled())

def process_feed(aFeed):
    if hasattr(aFeed, 'trayCountX'):
        return process_feed_tray(aFeed)
    if hasattr(aFeed, 'idealLineLocations'):
        return process_feed_strip(aFeed)
    else:
        print("Unsupported feed type\n")
        
    return None
        
def freeze_feeders():
    FeedInfoList = []
    feederList = psypnp.search.get_sorted_feeders_list()
    
    feeds_processed = 0
    if feederList is None or not len(feederList):
        return feeds_processed

    next_feeder_index = 0
    while next_feeder_index < len(feederList):
        nxtFeed = None
        while next_feeder_index < len(feederList) and nxtFeed is None:
            if feederList[next_feeder_index].isEnabled() and feederList[next_feeder_index].getPart() is not None:
                nxtFeed = feederList[next_feeder_index]
            next_feeder_index += 1
            
        if nxtFeed is not None:
            feedDetails = process_feed(nxtFeed)
            if feedDetails is not None:
                FeedInfoList.append(feedDetails)
                feeds_processed += 1
                
    if not IncludeDisabledOfSamePart:
        return FeedInfoList
    
    # need to do disabled feeds as well...
    # get map of enabled parts
    validParts = dict()
    for aFeedInfo in FeedInfoList:
        validParts[aFeedInfo.part.getId()] = True
        
    

    next_feeder_index = 0
    while next_feeder_index < len(feederList):
        nxtFeed = None
        while next_feeder_index < len(feederList) and nxtFeed is None:
            if not feederList[next_feeder_index].isEnabled():
                part = feederList[next_feeder_index].getPart()
                if part is not None and part.getId() in validParts:
                    nxtFeed = feederList[next_feeder_index]
            next_feeder_index += 1
            
        if nxtFeed is not None:
            feedDetails = process_feed(nxtFeed)
            if feedDetails is not None:
                feedDetails.disabled = True
                FeedInfoList.append(feedDetails)
                feeds_processed += 1
    

    return FeedInfoList
    
def generate_backup(feed_entries, projname, filename):
    if not len(feed_entries):
        psypnp.ui.showError("Nothing to save")
        return 0
    
    f = open(filename, 'w')
    w = csv_module.writer(f) 
    w.writerow(['#', '', str(projname)])
    colnames = feed_entries[0].CSVColumnNamesList()
    colnames[0] = '# %s' % colnames[0]
    w.writerow(colnames)
    for entry in feed_entries:
        w.writerow(entry.toCSVList())
        
    f.close()
    return len(feed_entries)
    
main()
