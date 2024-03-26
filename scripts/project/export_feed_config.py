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
import psypnp.debug
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
    
    
    sel = psypnp.getOption('Feeders Included', 'Include feeds', 
                           ['Only Enabled', 'All'])
    
    if sel is None:
        # aborted
        return 
    onlyEnabled = False
    if sel == 0:
        onlyEnabled = True 
    
    
    fmap = FeedMapper.FeedMapper(onlyEnabled)
    
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
    
    
    headersByType = {
            'strip': getHeadersStrip,
            'pushpull': getHeadersPushPull,
    }
    
    # first, figure out span of image
    psypnp.debug.out.flush("Generating CSVs for feeds:")
    for aFeed in feed_info:
        psypnp.debug.out.buffer(str(aFeed))
        psypnp.debug.out.buffer(', ')
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
    
    psypnp.debug.out.flush()
    # int-ify
    for i in range(0,2):
        x_range[i] = int(x_range[i])
        y_range[i] = int(y_range[i])
    
            
    psypnp.debug.out.flush("RANGE: %i,%i - %i,%i" % (
            x_range[0],
            y_range[0],
            x_range[1],
            y_range[1]))

    feedDescriptions = []
    
    partsRefMap = get_partreferences_map()
    
    globCountMap = dict()
    feedTypes = dict()
    with open(fname, 'w') as csvfile:
        psypnp.debug.out.flush('Opened file %s' % fname)
        csvwriter = csv_module.writer(csvfile, delimiter=',',
                            quotechar='"', quoting=csv_module.QUOTE_MINIMAL)
        
        
        
        # sorted_feedinfo = sorted(feed_info, key=lambda x: (x.part.getId(), x.feed.getName()))
        sorted_feedinfo = sorted(feed_info, key=lambda x: x.feed.getName())
        
        
        for aFeedInfo in sorted_feedinfo:
            feedTypes[aFeedInfo.type] = True
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
        for ft in feedTypes.keys():
            if ft in headersByType:
                csvwriter.writerow(headersByType[ft]())
        
        for f in sortedFeedDescs:
            f[partFeedCountTotalIdx] = globCountMap[f[partIdIndex]]
            csvwriter.writerow(f)
            psypnp.debug.out.flush(str(f))
        
    
    return len(feedDescriptions)
            
            
def getHeadersCommon():
    hdrs = [
        '# type',
        'set#',
        'of',
        'feed',
        '#/board',
        'ref',
        'part',
        'package',
        'part pitch',
        'feedcount',
        'retry'
    ]
    return hdrs

def getHeadersStrip():
    hdrs = getHeadersCommon()
    additionalStrip = [
        'holepitch',
        'max',
        'tapetype',
        'tapewidth',
        'locx',
        'locy',
        'locz',
        'locrot',
        'locunit',
        'refx',
        'refy',
        'refz',
        'refrot',
        'refunit'
    ]
    hdrs.extend(additionalStrip)
    hdrs[0] = '# STRIP'
    return hdrs

def getHeadersPushPull():
    
    hdrs = getHeadersCommon()
    additionalPushPull = [
        'feedpitch',
        'rotinfeeder',
        'startx',
        'starty',
        'startz',
        'startrot',
        'startunit',
        'mid1x',
        'mid1y',
        'mid1z',
        'mid1rot',
        'mid1unit',
        'mid2x',
        'mid2y',
        'mid2z',
        'mid2rot',
        'mid2unit',
        'mid3x',
        'mid3y',
        'mid3z',
        'mid3rot',
        'mid3unit',
        'endx',
        'endy',
        'endz',
        'endrot',
        'endunit',
        'deltax',
        'deltay',
        'speedpull0',
        'speedpull1',
        'speedpull2',
        'speedpull3',
        'speedpush1',
        'speedpush2',
        'speedpush3',
        'speedpushend',
        'incmulti0',
        'incmulti1',
        'incmulti2',
        'incmulti3',
        'incmultiend',
        
        'incpull0',
        'incpull1',
        'incpull2',
        'incpull3',
        
        'incpush1',
        'incpush2',
        'incpush3',
        'incpushend',
        
    ]
    hdrs.extend(additionalPushPull)
    hdrs[0] = '# PUSHPULL'
    return hdrs
    

def getCoordinatesFor(someLocation=None):
    if someLocation is None:
        return ['', '','','', '']
    
    retList = [
        someLocation.getX(),
        someLocation.getY(),
        someLocation.getZ(),
        someLocation.getRotation(),
        someLocation.getUnits().getShortName()
    ]
    return retList
    
def append_coordinates(aLocation, to_cols):
    to_cols.extend(getCoordinatesFor(aLocation))
    
def append_columns_pushpull(aFeed, to_cols):
    
    addenda = [
        aFeed.getFeedPitch().getValue(),
        aFeed.getRotationInFeeder()
    ]
    
    locations = [
        aFeed.getFeedStartLocation(),
        aFeed.getFeedMid1Location(),
        aFeed.getFeedMid2Location(),
        aFeed.getFeedMid3Location(),
        aFeed.getFeedEndLocation()
        
    ]
    speeds = [
                                                                        
        aFeed.getFeedSpeedPull0(),                                                                
        aFeed.getFeedSpeedPull1(),                                                                
        aFeed.getFeedSpeedPull2(),                                                            
        aFeed.getFeedSpeedPull3(),                                                            
        aFeed.getFeedSpeedPush1(),                                                           
        aFeed.getFeedSpeedPush2(),                                                          
        aFeed.getFeedSpeedPush3(),                                                          
        aFeed.getFeedSpeedPushEnd(), 
    ]
    
    included = [
                                                                           
        aFeed.isIncludedMulti0(),                                                    
        aFeed.isIncludedMulti1(),                                                  
        aFeed.isIncludedMulti2(),                                                 
        aFeed.isIncludedMulti3(),                                                
        aFeed.isIncludedMultiEnd(),                                              
        aFeed.isIncludedPull0(),                                              
        aFeed.isIncludedPull1(),                                              
        aFeed.isIncludedPull2(),                                             
        aFeed.isIncludedPull3(),                                             
        aFeed.isIncludedPush1(),                                             
        aFeed.isIncludedPush2(),                                            
        aFeed.isIncludedPush3(),                                            
        aFeed.isIncludedPushEnd()
        
        ]
    
    for loc in locations:
          append_coordinates(loc, addenda)
          
    deltax = []
    deltay = []
    for i in range(1, len(locations)):
        lb = locations[i]
        la = locations[i-1]
        deltax.append(str(lb.getX() - la.getX()))
        deltay.append(str(lb.getY() - la.getY()))
        
    addenda.append(' '.join(deltax))
    addenda.append(' '.join(deltay))
        
    
    addenda.extend(speeds)
    addenda.extend(included)
    to_cols.extend(addenda)

def append_columns_strip(aFeed, to_cols):
    
    addenda = [
        
        aFeed.getHolePitch().getValue(),
        aFeed.getMaxFeedCount(),
        aFeed.getTapeType().toString(),
        aFeed.getTapeWidth().getValue()
    ]
    
    append_coordinates(aFeed.getReferenceHoleLocation(), addenda)
    
    to_cols.extend(addenda)

        
    
def gather_columns(aFeedInfo, globCountMap, partsRefMap):
    
    extraProcessorsByType = {
            'strip': append_columns_strip,
            'pushpull': append_columns_pushpull,
    }
    
    
    aFeed = aFeedInfo.feed
    
    #loc = aFeed.getLocation()
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
    
    feedType = aFeedInfo.type
    cols =  [
        feedType,
        globCountMap[partName], # set index e.g. 2 of 4
        -1, # total slots for part, set later
        aFeed.getName(),
        numPartsPerBoard,
        ref,
        part.getId(),
        pkg.getId(),
        aFeed.getPartPitch(),
        aFeed.getFeedCount(),
        aFeed.getFeedRetryCount(),
        
    ]
    
    
    feederLocation = getCoordinatesFor(aFeed.getLocation())
    
    if feedType in extraProcessorsByType:
        addFunc = extraProcessorsByType[feedType]
        addFunc(aFeed, cols)

    return cols
    
try:
    main()
except:
    print(traceback.format_exc())
