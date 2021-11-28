'''
Generates a CSV file of the current state of enabled feeders.

This is useful in order to get a better idea of what's going on and,
more importantly for me, how to re-set the feeders for a batch of 
boards I've done before, when re-importing the config.

This basically just transforms the feed info mapped out by 
psypnp.feedmap.feedmapper into a CSV file, with enough info
to do setup but also potentially to re-import later.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/
--need to update this...

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

import datetime

from org.openpnp.model import Location, Length, LengthUnit 

import psypnp
import psypnp.nv # non-volatile storage
import psypnp.feedmap.feedmapper as FeedMapper
import psypnp.ui
import traceback
import csv as csv_module

StorageParentName = 'fdrexp'
ReferenceStringMaxLen = 25
    

def get_selected_boards():
    # I don't know any other way to get access to the blasted boards
    boardsList = psypnp.ui.getSelectedBoards()
    if boardsList is None or not len(boardsList):
        # psypnp.ui.showError("Select at least one board")
        return None
    return boardsList

def get_partreferences_map():
    boardsList = get_selected_boards()
    
    refsMap = dict()
    if boardsList is None or not len(boardsList):
        return refsMap
    
    for aBoard in boardsList:
        for aplacement in aBoard.getPlacements():
            part = aplacement.getPart()
            if part is None:
                continue 
            pid = part.getId()
            if pid not in refsMap:
                refsMap[pid] = []
            
            refsMap[pid].append(str(aplacement.getId()))
    
    return refsMap 

def main():
    
    lastProjName = psypnp.nv.get_subvalue(StorageParentName, 'projname')
    lastFileName = psypnp.nv.get_subvalue(StorageParentName, 'filename')
    if lastProjName is None:
        lastProjName = 'My Project'
        
    if lastFileName is None:
        lastFileName = 'feed_map.csv'
    
    fmap = FeedMapper.FeedMapper()
    feed_info = fmap.map()
    if feed_info is None or not len(feed_info):
        psypnp.showMessage("No enabled feeds to export")
        return
        
    projname = psypnp.getUserInput("Project Name", lastProjName)
    if projname is None:
       return
    fname = psypnp.getUserInput("Save as CSV file", lastFileName)
    if fname is None:
        return
        
    psypnp.nv.set_subvalue(StorageParentName, 'projname', projname, False)
    psypnp.nv.set_subvalue(StorageParentName, 'filename', fname)
    numFeeds = generate_csv(feed_info, projname, fname)
    psypnp.showMessage("Saved %i feeds to %s" % (numFeeds, fname))
    
    
def generate_csv(feed_info, projname, fname):
    x_range = [10000, -10000] # arbitrary large 'invalid' values
    y_range = [10000, -10000]
    
    # first, figure out span of image
    for aFeed in feed_info:
        x = aFeed.location.getX()
        y = aFeed.location.getY()
        if x < x_range[0]:
            x_range[0] = x
        if x > x_range[1]:
            x_range[1] = x
        if y < y_range[0]:
            y_range[0] = y
        if y > y_range[1]:
            y_range[1] = y
    
    # int-ify
    for i in range(0,2):
        x_range[i] = int(x_range[i])
        y_range[i] = int(y_range[i])
    
            
    print("RANGE: %i,%i - %i,%i" % (
            x_range[0],
            y_range[0],
            x_range[1],
            y_range[1]))

    feedDescriptions = []
    
    hdrs = [
        '# type',
        'set#',
        'of',
        'feed',
        '#/board',
        'ref',
        'part',
        'package',
        'pitch',
        'tape',
        'feedcount',
        'retry',
        'max',
        'locx',
        'locy',
        'locz',
        'locrot',
        'locunit',
        'refx',
        'refy',
        'refz',
        'refrot',
        'refunit',
    ]
    
    partsRefMap = get_partreferences_map()
    
    globCountMap = dict()
    with open(fname, 'w') as csvfile:
        csvwriter = csv_module.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv_module.QUOTE_MINIMAL)
        
        
        
        sorted_feedinfo = sorted(feed_info, key=lambda x: (x.part.getId(), x.feed.getName()))
        
        
        for aFeedInfo in sorted_feedinfo:
            feedDescriptions.append(
                gather_columns(aFeedInfo, globCountMap, partsRefMap))
        
        partFeedCountTotalIdx = 2
        partIdIndex = 6
        feedIdIndex = 3
        sortedFeedDescs = sorted(feedDescriptions, key=lambda x: (x[feedIdIndex], x[partIdIndex]))
        
        dtnow = datetime.datetime.now()
        
        firstline = ['#', '', '', projname, 
            '%s: %i feeds'  % (
                dtnow.strftime("%Y-%m-%d %H:%M:%S"),
                len(sortedFeedDescs)),
            '[(%i,%i) - (%i,%i)]' % (
                x_range[0],
                y_range[0],
                x_range[1],
                y_range[1])
        ]
        
        csvwriter.writerow(firstline)
        csvwriter.writerow(hdrs)
        for f in sortedFeedDescs:
            f[partFeedCountTotalIdx] = globCountMap[f[partIdIndex]]
            csvwriter.writerow(f)
        
    
    return len(feedDescriptions)
            
    
def gather_columns(aFeedInfo, globCountMap, partsRefMap):
    aFeed = aFeedInfo.feed
    refHole = aFeed.getReferenceHoleLocation()
    loc = aFeed.getLocation()
    part = aFeedInfo.part 
    pkg = part.getPackage()
    
    partName = part.getId()
    numPartsPerBoard = 0
    if partName in partsRefMap:
        numPartsPerBoard = len(partsRefMap[partName])
        ref = ' '.join(partsRefMap[partName])
        if len(ref) > ReferenceStringMaxLen:
            ref = ref[:ReferenceStringMaxLen] + '...'
            
        
    else:
        ref = ''
        
    # keep a running tab of part, and 
    # use this as the index for the set
    if partName in globCountMap:
        globCountMap[partName] += 1
    else:
        globCountMap[partName] = 1
        
    return [
        aFeedInfo.type,
        globCountMap[partName], # set index e.g. 2 of 4
        -1, # total slots for part, set later
        aFeed.getName(),
        numPartsPerBoard,
        ref,
        part.getId(),
        pkg.getId(),
        aFeed.getPartPitch(),
        aFeed.getTapeType().toString(),
        aFeed.getFeedCount(),
        aFeed.getFeedRetryCount(),
        aFeed.getMaxFeedCount(),
        loc.getX(),
        loc.getY(),
        loc.getZ(),
        loc.getRotation(),
        loc.getUnits().getShortName(),
        refHole.getX(),
        refHole.getY(),
        refHole.getZ(),
        refHole.getRotation(),
        refHole.getUnits().getShortName(),
    ]
    
    
try:
    main()
except:
    print(traceback.format_exc())
