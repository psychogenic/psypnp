'''
Generates an (SVG) image of the current state of enabled feeders.

This is useful in order to get a better idea of what's going on and,
more importantly for me, how to re-set the feeders for a batch of 
boards I've done before, when re-importing the config.

This basically just transforms the feed info mapped out by 
psypnp.feedmap.feedmapper into an SVG.

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

import re
from org.openpnp.model import Location, Length, LengthUnit 

import psypnp
import psypnp.nv # non-volatile storage
import psypnp.feedmap.feedmapper as FeedMapper



SVGWriteImported = True
SVGWriteImportError = ''
try:
    import svgwrite
    import math
except Exception as e:
    SVGWriteImportError = str(e)
    SVGWriteImported = False
    

StorageParentName = 'fdrmap'
IncludeFeedNameInDesc = True
CleanupFeedPartName = True
ImageScaleFactor = 5
ImageMargins = 2000
FontSize = 32
FontSpacingShrink = 3
IncludeDisabledOfSamePart = False
FontStyle="font-family: Arial, Helvetica, sans-serif;"
FontStyle="font-family: monospace, sans-serif;"
ArrowOffset = FontSize*2.5
ArrowSideLength = FontSize
BoxColour = 'cadetblue'
ArrowColour = 'darkcyan'


    

def main():
    
    if not SVGWriteImported:
        psypnp.showMessage("Could not import svgwrite lib, aborting\n%s" % SVGWriteImportError)
        return
    
    lastProjName = psypnp.nv.get_subvalue(StorageParentName, 'projname')
    lastFileName = psypnp.nv.get_subvalue(StorageParentName, 'filename')
    if lastProjName is None:
        lastProjName = 'My Project'
        
    if lastFileName is None:
        lastFileName = 'feed_map.svg'
    
    fmap = FeedMapper.FeedMapper()
    feed_info = fmap.map()
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
    partName = aFeedInfo.part.getId()
    
    if CleanupFeedPartName:
        partName = re.sub(r'_\d+Metric-', ' ', partName)
        
    if IncludeFeedNameInDesc:
        txtVal = '%s [%s]  ' % (aFeedInfo.name, partName)
    else:
        txtVal = partName
        
    return txtVal.replace('_', ' ')
    
    
    

def distance_per_letter():
    return FontSize - FontSpacingShrink
    
def text_length_dim(strval):
    return (len(strval) * distance_per_letter())
    
    
def breathing_room_distance():
    return (distance_per_letter() * 10)
    
def generate_feed(dwg, aFeed, x_realoffset, y_realoffset, imgdimX, imgdimY):
    feedTxt = text_for_feedinfo(aFeed)
    base_x = map_coord_to_imagespace(aFeed.location.getX(), x_realoffset)
    base_y = coord_flip_y(map_coord_to_imagespace(aFeed.location.getY(), y_realoffset), imgdimY)
    
    print("Base coords for feed %s are (%s,%s)" % (
        aFeed.name, 
        str(base_x),
        str(base_y)
        ))
    
    dy = 0
    dx = 0
    rot = 0
    boxsize = [int(FontSize*1.5), int(FontSize*1.5)]
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
            base_x = base_x - breathing_room_distance()
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
        boxsize[0] = text_size + FontSize + (5*FontSpacingShrink)
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
            base_y = base_y - breathing_room_distance()
            rot = 90
            boxpos=[base_x - 2, base_y - text_size]
            arrowpoints = [
            	(base_x, base_y + ArrowOffset),
            	(base_x + delta_arrow, base_y + ArrowOffset - delta_arrow),
            	(base_x + (2*delta_arrow), base_y + ArrowOffset),
            	(base_x, base_y + ArrowOffset)
           ]
        boxsize[1] = text_size + FontSize + (5*FontSpacingShrink)
    
    
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
    box = dwg.rect(boxpos, boxsize, fill=boxFill, stroke_width="3", stroke=BoxColour)
    
    arrlines = None
    if len(arrowpoints):
        arrlines = dwg.add(dwg.g(id='arrow-%i' % aFeed.fid, stroke_width=2, stroke=ArrowColour))
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



    
main()
