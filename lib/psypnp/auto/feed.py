'''
Created on Oct 15, 2020

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

import psypnp.globals
import psypnp.csv_file
import psypnp.debug

from org.openpnp.model import Location
from org.openpnp.machine.reference.feeder import ReferenceStripFeeder, ReferencePushPullFeeder
from psypnp.auto.feedsets import FeedSet, SystemFeeds


# TODO: FIXME hard-coded stuff here
# name distance to consider feeds part of a set
FeedSetNameMaxDistance = 3



def feed_type_supported(aFeed):
    '''
        return bool True if we can handle this openpnp feed
        type.
        @note: currently only supports ReferenceStripFeeder.
    '''
    if aFeed is None or not hasattr(aFeed, 'getClass'):
        return False
    c = aFeed.getClass()
    
    # only supporting strip and push-pull feeders at this point.
    if c == ReferenceStripFeeder:
        return True
    if c == ReferencePushPullFeeder:
        return True 
    return False 

def get_feed_location(aFeed):
    ''' 
        @note: currently only supports things that have getReferenceHoleLocation()
               or getHole1Location
        @return: a Location for this feed, used for distance calculations.
    '''
    # idea here is to abstract this function in a way
    # to eventually be able to support extra feed types.
    
    if hasattr(aFeed, 'getReferenceHoleLocation'):
        return aFeed.getReferenceHoleLocation()
    
    if hasattr(aFeed, 'getHole1Location'):
        return aFeed.getHole1Location()
    
    return None

def workspace_centroid():
    '''
        workspace_centroid find a spot that is in the "middle" of all 
        feed locations.
    '''
    x_tot = 0
    y_tot = 0
    feed_count = 0
    unit_used = None
    for aFeed in psypnp.globals.machine().getFeeders():
        
        if aFeed and feed_type_supported(aFeed):
            loc = get_feed_location(aFeed) 
            if loc is None:
                continue
            
            #print(str(loc))
            feed_count += 1
            x_tot += loc.getX()
            y_tot += loc.getY()
            if unit_used is None:
                unit_used = loc.getUnits()
                #print(str(unit_used))
                
    if feed_count < 2:
        return None
    
    return Location(unit_used, x_tot/feed_count, y_tot/feed_count, 0, 0)
            
def feeds_by_distance():
    '''
        provides a list of tuples [(FEED, DISTANCE)...] 
        where DISTANCE is distance from the workspace feed centroid,
        that is sorted by distance.
    '''
    centroid = workspace_centroid()
    retList = []
    if centroid is None:
        return retList
    
    distList = []
    for aFeed in psypnp.globals.machine().getFeeders():
        #print(str(aFeed))
        if aFeed and feed_type_supported(aFeed):
            loc = get_feed_location(aFeed)
            if loc is not None:
                distList.append(  (aFeed, centroid.getLinearDistanceTo(loc) ) )
            
    sList = sorted(distList, key=lambda tup: tup[1])
    return sList

def feed_name_distance(feed1, feed2):
    '''
        Calculates the "distance" between two feed names, where 
        returning 1 would mean a single letter difference, etc.
    '''
    n1 = feed1.getName()
    n2 = feed2.getName()
    
    len_1 = len(n1)
    len_2 = len(n2)
    max_len = len_1 if len_1 > len_2 else len_2
    
    for i in range(max_len):
        if i >= len_1 or i >= len_2:
            return max_len - i 
        
        if n1[i] != n2[i]:
            return max_len - i 
        
    return 0
        
    

def feed_sets():
    '''
        feed_sets
        Returns a SystemFeeds instance, which holds some number of 
        FeedSet entries, which in turn will hold the actual openpnp feeds.
        
        These sets are used to group individual feeds based on their _name_
        so this system assumes you are using some sane naming convention.
        
        In my case, I have stuff like
        8mmRight_01
        8mmRight_02
        8mmRight_03...
        
        8mmLeft_01
        8mmLeft_02...
        
        12mmTop_01 etc
        
        which, I would hope, is pretty self-explanatory and allows this system
        to work.
    '''
    sysfeeds = SystemFeeds()
    
    for aFeed in psypnp.globals.machine().getFeeders():
        if not feed_type_supported(aFeed):
            continue
        psypnp.debug.out.buffer("Doing %s" % str(aFeed))
        foundHome = False
        for feedSet in sysfeeds.entries():
            #print("Doing feedset %s" % setName)
            for feed in feedSet.entries():
                if feed_name_distance(feed, aFeed) <= FeedSetNameMaxDistance and not foundHome:
                    psypnp.debug.out.flush("is close to %s" % str(aFeed))
                    feedSet.append(aFeed)
                    foundHome = True
                    continue
    
        if not foundHome:
            psypnp.debug.out.flush("Creating new feed set for %s" % aFeed.getName())
            newFSet = FeedSet(aFeed.getName())
            newFSet.append(aFeed)
            sysfeeds.append(newFSet)
    
    
    return sysfeeds
                    
        
