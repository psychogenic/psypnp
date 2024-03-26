'''
Created on Nov 20, 2021

Feed mapping utilities, for generating maps and exports.


@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/


Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''
import psypnp.globals

class FeedInfo:
    FeedIdCounter = 0
    def __init__(self, feedObj, stype, name, loc, travelX, travelY, part, disabled=False):
        self.fid = FeedInfo.FeedIdCounter
        FeedInfo.FeedIdCounter += 1
        self.feed = feedObj
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
    def __init__(self, feedObj, name, loc, travelX, travelY, part, disabled=False):
        # ugh, py2.? inheritance, super not working
        FeedInfo.__init__(self, feedObj, 'tray', name, loc, travelX, travelY, part, disabled)
        self.x_count = 1
        self.y_count = 1
        
        
        
class StripFeedInfo(FeedInfo):
    def __init__(self, feedObj, name, loc, travelX, travelY, part, disabled=False):
        FeedInfo.__init__(self, feedObj, 'strip', name, loc, travelX, travelY, part, disabled)
    
        
        
class PushPullFeedInfo(FeedInfo):
    def __init__(self, feedObj, name, loc, travelX, travelY, part, disabled=False):
        FeedInfo.__init__(self, feedObj, 'pushpull', name, loc, travelX, travelY, part, disabled)
    

class FeedMapper:
        
    def __init__(self, onlyEnabled=True):
        self.include_only_enabled = onlyEnabled
        self.include_disabled_of_samepart = False
        self.feedInfoList = []
        
    
    def map(self):
        feederList = psypnp.globals.machine().getFeeders()
        self.feedInfoList = []
        feeds_processed = 0
        if feederList is None or not len(feederList):
            return feeds_processed
    
        next_feeder_index = 0
        while next_feeder_index < len(feederList):
            nxtFeed = None
            while next_feeder_index < len(feederList) and nxtFeed is None:
                if feederList[next_feeder_index].isEnabled() or not self.include_only_enabled:
                    if feederList[next_feeder_index].getPart() is not None:
                        nxtFeed = feederList[next_feeder_index]
                next_feeder_index += 1
                
            if nxtFeed is not None:
                feedDetails = self.process_feed(nxtFeed)
                if feedDetails is not None:
                    self.feedInfoList.append(feedDetails)
                    feeds_processed += 1
                    
        if not self.include_disabled_of_samepart:
            return self.feedInfoList
        
        # need to do disabled feeds as well...
        # get map of enabled parts
        validParts = dict()
        for aFeedInfo in self.feedInfoList:
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
                feedDetails = self.process_feed(nxtFeed)
                if feedDetails is not None:
                    feedDetails.disabled = True
                    self.feedInfoList.append(feedDetails)
                    feeds_processed += 1
    
        return self.feedInfoList
    
    
    def process_feed_tray(self, aFeed):
        print("TODO: trays not really supported yet\n")
        offsets = aFeed.getOffsets()
        deltaX = offsets.getX()
        deltaY = offsets.getY()
        tFeed =  TrayFeedInfo(aFeed, aFeed.getName(), 
                              aFeed.getPickLocation(), 
                              deltaX, deltaY, aFeed.getPart())
        tFeed.x_count = aFeed.getTrayCountX()
        tFeed.y_count = aFeed.getTrayCountY()
        
        return tFeed
        
        
    def process_feed_pushpull(self, aFeed):
        return PushPullFeedInfo(aFeed, aFeed.getName(),
                                aFeed.getLocation(), -1, 0, aFeed.getPart())
        
    def process_feed_strip(self, aFeed):
        idealLines = aFeed.idealLineLocations
        if idealLines is None or len(idealLines) < 2:
            return False
        
        deltaX = idealLines[1].getX() - idealLines[0].getX()
        deltaY = idealLines[1].getY() - idealLines[0].getY()
        if abs(deltaX) > abs(deltaY):
            # is X dir, assume pure X
            return StripFeedInfo(aFeed, aFeed.getName(), 
                                 aFeed.getReferenceHoleLocation(), 
                                 deltaX, 0, aFeed.getPart())
        
        # assume pure Y
        return StripFeedInfo(aFeed, aFeed.getName(), 
                             aFeed.getReferenceHoleLocation(), 
                             0, deltaY, aFeed.getPart())
    
    def process_feed(self, aFeed):
        #if hasattr(aFeed, 'trayCountX'):
        #    return self.process_feed_tray(aFeed)
        
        
        if hasattr(aFeed, 'toString'):
            asStr = aFeed.toString() 
            if asStr.find('Strip') >= 0:
                return self.process_feed_strip(aFeed)
            if asStr.find('PushPull') >= 0:
                return self.process_feed_pushpull(aFeed)
            
            
        if hasattr(aFeed, 'idealLineLocations'):
            return self.process_feed_strip(aFeed)
            
        else:
            print("Unsupported feed type\n")
            
        return None