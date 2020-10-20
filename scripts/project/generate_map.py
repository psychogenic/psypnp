'''
Generates an (SVG) image of the current state of enabled feeders.

This is useful in order to get a better idea of what's going on and,
more importantly for me, how to re-set the feeders for a batch of 
boards I've done before, when re-importing the config.

@note: you need to have installed the compatible version of 
svgwrite for this to work. See the project page for deets:

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

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

import psypnp
import psypnp.nv # non-volatile storage



SVGWriteImported = True
try:
    import svgwrite
    import math
except:
    SVGWriteImported = False
    

StorageParentName = 'fdrmap'
IncludeFeedNameInDesc = False
ImageScaleFactor = 5
ImageMargins = 1100
FontSize = 24
IncludeDisabledOfSamePart = False
FontStyle="font-family: Arial, Helvetica, sans-serif;"
ArrowOffset = FontSize*2
ArrowSideLength = 20
ArrowColour = 'green'

FeedIdCounter = 0

class FeedInfo:
    def __init__(self, stype, name, loc, travelX, travelY, part, disabled=False):
        global FeedIdCounter
        self.fid = FeedIdCounter
        FeedIdCounter += 1
        self.type = stype
        self.name = name
        self.location = loc
        self.deltaX = travelX
        self.deltaY = travelY
        self.part = part
        self.disabled = disabled
    def toString(self):
        return "%s (%s) [%s, %s] for %s" % (self.name,
        	self.type,
        	str(self.deltaX),
        	str(self.deltaY),
        	self.part.getId())
    
    def __str__(self):
        return "Feed %s" % self.toString()
        
    def __repr__(self):
        return "<FeedInfo %s>" % self.toString()
        
        
class TrayFeedInfo(FeedInfo):
    def __init__(self, name, loc, travelX, travelY, part, disabled=False):
        # ugh, py2.? inheritance, super not working
        FeedInfo.__init__(self, 'tray', name, loc, travelX, travelY, part, disabled)
        self.x_count = 1
        self.y_count = 1
        
        
        
class StripFeedInfo(FeedInfo):
    def __init__(self, name, loc, travelX, travelY, part, disabled=False):
        FeedInfo.__init__(self, 'strip', name, loc, travelX, travelY, part, disabled)
    
        
    

def main():
    
    if not SVGWriteImported:
        psypnp.showMessage("Could not import svgwrite lib, aborting")
        return
    
    lastProjName = psypnp.nv.get_subvalue(StorageParentName, 'projname')
    lastFileName = psypnp.nv.get_subvalue(StorageParentName, 'filename')
    if lastProjName is None:
        lastProjName = 'My Project'
        
    if lastFileName is None:
        lastFileName = 'feed_map.svg'
        
    feed_info = map_feeders()
    if feed_info is None or not len(feed_info):
        psypnp.showMessage("No enabled feeds to map")
        return
        
    projname = psypnp.getUserInput("Name of map", lastProjName)
    if projname is None:
       return
    fname = psypnp.getUserInput("Save as SVG file", lastFileName)
    if fname is None:
        return
        
    psypnp.nv.set_subvalue(StorageParentName, 'projname', projname, False)
    psypnp.nv.set_subvalue(StorageParentName, 'filename', fname)
    numFeeds = generate_image(feed_info, projname, fname)
    psypnp.showMessage("Saved %i feeds to %s" % (numFeeds, fname))


def coord_flip_y(ycoord, ysize):
    return ysize - ycoord

def map_coord_to_imagespace(c, offset):
    return ((c - offset) * ImageScaleFactor) + ImageMargins
    
def text_for_feedinfo(aFeedInfo):
    if IncludeFeedNameInDesc:
        return '%s (%s)' % (aFeedInfo.name, aFeedInfo.part.getId())
    
    return aFeedInfo.part.getId()
    

def distance_per_letter():
    return FontSize - 2
    
def text_length_dim(strval):
    return (len(strval) * distance_per_letter())
    
    
def generate_feed(dwg, aFeed, x_realoffset, y_realoffset, imgdimX, imgdimY):
    feedTxt = text_for_feedinfo(aFeed)
    base_x = map_coord_to_imagespace(aFeed.location.getX(), x_realoffset)
    base_y = coord_flip_y(map_coord_to_imagespace(aFeed.location.getY(), y_realoffset), imgdimY)
    
    dy = 0
    dx = 0
    rot = 0
    boxsize = [FontSize + 5, FontSize+5]
    boxpos = [20, 20]
    
    delta_arrow = math.sqrt((ArrowSideLength**2)/2)
    text_size = text_length_dim(feedTxt)
    arrowpoints = []
    if aFeed.deltaY == 0:
        # horizontal
        if aFeed.deltaX < 0:
            # going left
            dx = (-1 * distance_per_letter())
            feedTxt = feedTxt[::-1]
            boxpos = [base_x - text_size, base_y - FontSize]
            arrowpoints = [
            	(base_x + ArrowOffset, base_y),
            	(base_x + ArrowOffset - delta_arrow, base_y - delta_arrow),
            	(base_x + ArrowOffset, base_y - (2*delta_arrow)),
            	(base_x + ArrowOffset, base_y)
           ]
        else:
            dx = FontSize-2
            boxpos = [base_x - FontSize, base_y - FontSize]
            arrowpoints = [
            	(base_x - ArrowOffset, base_y),
            	(base_x - ArrowOffset + delta_arrow, base_y - delta_arrow),
            	(base_x - ArrowOffset, base_y - (2*delta_arrow)),
            	(base_x - ArrowOffset, base_y)
           ]
        boxsize[0] = text_size + FontSize
    else:
        if aFeed.deltaY < 0:
            # going down
            dy = distance_per_letter()
            rot = 270
            boxpos = [base_x, base_y]
            arrowpoints = [
            	(base_x, base_y - ArrowOffset),
            	(base_x + delta_arrow, base_y - ArrowOffset + delta_arrow),
            	(base_x + (2*delta_arrow), base_y - ArrowOffset),
            	(base_x, base_y - ArrowOffset)
           ]
        else:
            dy = -1 * distance_per_letter()
            feedTxt = feedTxt[::-1]
            base_y = base_y - text_size
            rot = 90
            boxpos=[base_x - 2, base_y - text_size]
            arrowpoints = [
            	(base_x, base_y + ArrowOffset),
            	(base_x + delta_arrow, base_y + ArrowOffset - delta_arrow),
            	(base_x + (2*delta_arrow), base_y + ArrowOffset),
            	(base_x, base_y + ArrowOffset)
           ]
        boxsize[1] = text_size + FontSize
    
    
    xcoords = []
    ycoords = []
    letter_count = 0
    for letter_count in range(0, len(feedTxt) + 1):
        xcoords.append(base_x + (letter_count * dx))
        ycoords.append(base_y + (letter_count * dy))
        
    txt =  dwg.text(feedTxt, x=xcoords, y=ycoords, rotate=[rot], style=FontStyle)
    boxFill = 'none'
    if aFeed.disabled:
        boxFill='red'
    box = dwg.rect(boxpos, boxsize, stroke='black', fill=boxFill)
    
    arrlines = None
    if len(arrowpoints):
    	arrlines = dwg.add(dwg.g(id='arrow-%i' % aFeed.fid, stroke=ArrowColour))
        lastPoint = None
        for aPoint in arrowpoints:
            if lastPoint:
                # print("ADDING POINT %s - %s" % (str(lastPoint), str(aPoint)))
                arrlines.add(dwg.line(start=lastPoint, end=aPoint))
            lastPoint = aPoint
    
    
    return [box, txt, arrlines]
    
    
def generate_image(feed_info, projname, fname):
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
    
    # calculate image size
    xsize = ((x_range[1] - x_range[0]) * ImageScaleFactor) + 2*ImageMargins
    ysize = ((y_range[1] - y_range[0]) * ImageScaleFactor) + 2*ImageMargins
    x_realoffset = x_range[0]
    y_realoffset = y_range[0]
    
    #print("SIZE : %ix%i" % (xsize, ysize))
    # create the drawing
    dwg = svgwrite.Drawing(fname, (xsize, ysize), debug=True)
    
    title = dwg.add(dwg.g(font_size=FontSize * 3))
    title.add(dwg.text(projname, insert=(20, 20+(FontSize * 3)), style=FontStyle))
    
    for aFeed in feed_info:
        elements = generate_feed(dwg, aFeed, x_realoffset, y_realoffset, xsize, ysize)
        paragraph = dwg.add(dwg.g(id='feed-%i' % aFeed.fid, font_size=FontSize))
        for el in elements:
            if el is not None:
                paragraph.add(el)
        
    dwg.save()
    return len(feed_info)

    
def process_feed_tray(aFeed):
    print("TODO: trays not really supported yet\n")
    offsets = aFeed.getOffsets()
    deltaX = offsets.getX()
    deltaY = offsets.getY()
    tFeed =  TrayFeedInfo(aFeed.getName(), aFeed.getPickLocation(), deltaX, deltaY, aFeed.getPart())
    tFeed.x_count = aFeed.getTrayCountX()
    tFeed.y_count = aFeed.getTrayCountY()
    
    return tFeed
    
    

    
def process_feed_strip(aFeed):
    idealLines = aFeed.idealLineLocations
    if idealLines is None or len(idealLines) < 2:
        return False
    
    deltaX = idealLines[1].getX() - idealLines[0].getX()
    deltaY = idealLines[1].getY() - idealLines[0].getY()
    if abs(deltaX) > abs(deltaY):
        # is X dir, assume pure X
        return StripFeedInfo(aFeed.getName(), aFeed.getReferenceHoleLocation(), deltaX, 0, aFeed.getPart())
    
    # assume pure Y
    return StripFeedInfo(aFeed.getName(), aFeed.getReferenceHoleLocation(), 0, deltaY, aFeed.getPart())

def process_feed(aFeed):
    if hasattr(aFeed, 'trayCountX'):
        return process_feed_tray(aFeed)
    if hasattr(aFeed, 'idealLineLocations'):
        return process_feed_strip(aFeed)
    else:
        print("Unsupported feed type\n")
        
    return None
        
def map_feeders():
    FeedInfoList = []
    feederList = machine.getFeeders()
    
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
    
main()
