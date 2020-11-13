'''
Created on Oct 16, 2020


Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''
import psypnp.debug 
import math


class WorkspaceMapper:
    def __init__(self, wspace): # (psypnp.project.workspace)
        
        # keep a handle on our calling workspace
        self.workspace = wspace 
        # re-map the workspace object(s) for simple access
        self.feed_sets = wspace.feeds.sets 
        
                    
    def isReady(self):
        # to be ready, we need the workspace to be so and for it to 
        # have a project associated
        return self.workspace.isReady() and self.workspace.project is not None
    
    def find_feedset_for(self, projPart, inqty):
        psypnp.debug.out.buffer("Searching for feedset for %s" % str(projPart))
        
        # check each set we have to see if it "prefers" this part package 
        # Preference is based on having such packages in the set already
        # either exclusively, or a majority of occupied feeds
        for feedSet in self.feed_sets.entries():
            # if its preferred AND there's actually enough space, we're done
            if feedSet.prefersPackage(projPart.package_description):
                if feedSet.hasSpaceFor(inqty, projPart.package_description):
                    psypnp.debug.out.buffer("Feedset %s CAN (PREFERED) hold %i %s" % (feedSet, inqty, projPart.package_description))
                    return feedSet
        
        # ok no one prefers
        # choose by distance, preferring empty sets over close ones, in order to 
        # seed a new set with a preference for this "rejected" package type
        psypnp.debug.out.buffer("no prefs stated, will look for closest available")
        feedsetsWithDistance = []
        for feedSet in self.feed_sets.entries():
            closestFeedInThisSet = feedSet.findNearestAvailableFeed()
            # only count sets that actually have space for us
            if feedSet.hasSpaceFor(inqty, projPart.package_description):
                feedsetsWithDistance.append((closestFeedInThisSet.distance_from_centroid, feedSet))
                
        # sort them by distance
        feedsetsByDistance = sorted(feedsetsWithDistance, key=lambda deets: deets[0])
        
        # go over the available sets, in order, and return
        # anything that is currently empty
        for feedSetTuple in feedsetsByDistance:
            fs = feedSetTuple[1]
            if fs.numEntriesReserved() == 0:
                psypnp.debug.out.buffer("Found closest EMPTY feedset")
                # a completely free feedset!
                return fs 
        
        psypnp.debug.out.buffer("No empty feedsets available, using closest")
        # none were completely free of reservations, just return closest.
        return feedsetsByDistance[0][1]
                
        
    def map(self, num_boards=4):
        '''
            For each part that we've mapped, 
            try to locate a feedset that will have enough feeds that accept to hold
            this type of part/package.  
            Once we have that set, reserve the closest of the feeds within (relative 
            to the workspace centroid) and as many neighbours as needed to hold 
            num_boards worth of parts.
            
        '''
        
        if not self.isReady():
            psypnp.debug.out.flush("Not READY to map()")
            return 
        
        part_map = self.workspace.project.part_map

        
        num_associated = 0 # counter for number of feeds we ate up 
        for apart in part_map.parts:
            #psypnp.debug.out.crumb('map')
            psypnp.debug.out.buffer("Attempting to map part %s" % str(apart))
            if apart.package_description is None:
                psypnp.debug.out.flush("Can't place part (%s) -- no package associated" % str(apart))
                continue
            
            
            # find a feedset that can carry the load of whatever 
            # the total quantity is for a batch
            total_qty = apart.quantity() * num_boards
            
            # magic happens in find_feedset_for (above)
            feedset = self.find_feedset_for(apart, total_qty)
            if feedset is None:
                psypnp.debug.out.flush("No space found for part %s" % str(apart))
                continue
            
            # have space! get the nearest available feed from this set
            closestFeed = feedset.findNearestAvailableFeed()
            if closestFeed is None:
                psypnp.debug.out.flush("Have space but NO closest feed???")
                continue
            
            # now we'd like to reserve enough neighbouring feeds to hold 
            # a suitable number of strips for x boards
            numPerFeed = closestFeed.holdsUpTo(apart.package_description)
            # based on how many this feed can hold, we figure out total strips
            # needed
            numFeedsNeeded = math.ceil((1.0*total_qty)/numPerFeed)
            
            # now can getNeighbours() on the feed set, using our closest feed as 
            # the seed
            neighbourFeeds = feedset.getNeighbours(closestFeed, numFeedsNeeded)
            # that should be a list containing at least our "seed" feed, maybe more
            if neighbourFeeds and len(neighbourFeeds):
                # reserve them all by calling setPart on them
                for feedToReserve in neighbourFeeds:
                    num_associated += 1
                    psypnp.debug.out.buffer("Reserving feed %s for part %s" % (str(feedToReserve), str(apart)))
                    feedToReserve.setPart(apart, apart.package_description)
            
            #psypnp.debug.out.clearCrumb('map')
            psypnp.debug.out.flush("Mapped to %i slots" % num_associated)
            
        return num_associated
    
    def compress(self):
        # get rid of empty spaces between occupied feeds
        self.feed_sets.compress()
        
    def apply(self):
        self.workspace.feeds.apply()
        
    
    def dump(self):
        self.workspace.feeds.dump()
        
            
    #def sourceFiles(self):
    #    return (self.part_map.bom_csv, self.package_descriptions, self.feed_descriptions)
    
    
    def __string__(self):
        return ' mapping "%s"' % (str(self.workspace.project))
    
    def __repr__(self):
        return '<WorkspaceMapper %s>' % self.__string__()
    
    