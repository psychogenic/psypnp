'''
Created on Oct 16, 2020


Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''
import psypnp.debug 
import math

class FeedSelectionDetails:
    def __init__(self, parentFeedSet, 
                 statedPreferenceForPkg,
                 distanceFromCentroid, 
                 partQty,
                 numSlotsRequired,
                 numPartsPerSlot):
        self.feedSet = parentFeedSet
        self.hasPreference = statedPreferenceForPkg
        self.distance = distanceFromCentroid
        self.partQuantity = partQty
        self.numSlots = numSlotsRequired
        self.numPartsPerSlot = numPartsPerSlot
        
    def spaceWasted(self):
        return self.partQuantity % self.numPartsPerSlot 
    
    def spaceWastedPercent(self):
        spwasted = self.spaceWasted()
        return (100.0 * spwasted / self.numPartsPerSlot)

class WorkspaceMapper:
    def __init__(self, wspace): # (psypnp.project.workspace)
        
        # keep a handle on our calling workspace
        self.workspace = wspace 
        # re-map the workspace object(s) for simple access
        self.feed_sets = wspace.feeds.sets 
        self.num_unplaced = 0
        self.allow_part_spreading = True # allow a part to be spread amongst multiple feed sets
        
    def numUnassociated(self):
        return self.num_unplaced
                    
    def isReady(self):
        # to be ready, we need the workspace to be so and for it to 
        # have a project associated
        return self.workspace.isReady() and self.workspace.project is not None
    
    def outputFSSearchDebug(self, msg, projPart, feedSelectionDeets):
        psypnp.debug.out.flush("\nFSSearch: %s\n %s for part %s (%i slots, %i/slot, free: %0.2f%%)" % 
                                           (
                                               msg,
                                               str(feedSelectionDeets.feedSet),
                                               str(projPart),
                                               feedSelectionDeets.numSlots,
                                               feedSelectionDeets.numPartsPerSlot,
                                               feedSelectionDeets.spaceWasted()
                                            ))
        return
    
    def find_feedset_for(self, projPart, inqty):
        psypnp.debug.out.buffer("Searching for feedset for %s" % str(projPart))
        
        numPrefSets = 0 # keep track of if _any_ sets already prefer this type
        feedsetSelDetails = []
        for feedSet in self.feed_sets.entries():
            closestFeedInThisSet = feedSet.findNearestAvailableFeed()
            # only count sets that actually have space for us
            numSlotsTaken = feedSet.numFeedsFor(inqty, 
                                                projPart.package_description)
            if numSlotsTaken: # 0 indicates can't fit here
                statedPref = feedSet.prefersPackage(projPart.package_description)
                if statedPref:
                    numPrefSets += 1
                # ok, can accept this part by eating up numSlotsTaken
                feedsetSelDetails.append(FeedSelectionDetails(feedSet, 
                                    statedPref,
                                    closestFeedInThisSet.distance_from_centroid, 
                                    inqty,
                                    numSlotsTaken, 
                                    feedSet.spacePerFeedFor(
                                        projPart.package_description)))
        
        if not len(feedsetSelDetails):
            psypnp.debug.out.buffer("find_feedset_for: no room in single feed!")
            return None
        
        # sort them by: 
        #  - preference (have to _not_ to get True first)
        #  - number of slots required (less is better)
        #  - amount of space left over (less is better)
        #  - distance -- we care, but only as a final determinant
        feedSetsByPriority = sorted(feedsetSelDetails, 
                                    key = lambda x: (not x.hasPreference, 
                                                     x.numSlots, 
                                                     x.spaceWasted(), 
                                                     x.distance))
        
        # if anyone has a preference for this package type, check if 
        # we can find a decent fit within that subset first
        if numPrefSets:
            # scenarioA: an 0402 can fit in either
            #   -  two feeds of a long feeder, leaving the 2nd 30% empty
            #   -  five feeds of a short one, leaving it only 2% empty
            # scenarioB: an 0603 takes only one slot, in either of 2
            #   -  one slot of a long feeder, leaving 40% empty
            #   -  one slot of a short feeder, leaving 1% empty
            # which is better?
            # In the latter case, the short (least waste) is obviously best
            # in the former, least amount of slots taken is better (so I say,
            # anyway)
            # they are already sorted by number of slots, and waste second
            # so the first available prefered feed should be fine
            # EXCEPT in the case where we've prefered a long feeder for part 1
            # and the second part would fit in there but waste a lot of space
            # and could fit in another free set
            # prefSets = []
            if numPrefSets < 2 and len(feedSetsByPriority) > 1:
                # this is a case where we've only started packing one feed
                # set, should check for less wasteful free set
                if feedSetsByPriority[1].numSlots == \
                    feedSetsByPriority[1].numSlots and \
                    feedSetsByPriority[1].spaceWasted() < feedSetsByPriority[0].spaceWasted():
                    self.outputFSSearchDebug('Better than preferred', projPart, feedSetsByPriority[1])
                    return feedSetsByPriority[1].feedSet
            
                
            
            
            self.outputFSSearchDebug('PREF', projPart, feedSetsByPriority[0])
            return feedSetsByPriority[0].feedSet
            
        
        # ok no one prefers
        # choose by distance, preferring empty sets over close ones, in order to 
        # seed a new set with a preference for this "rejected" package type
        psypnp.debug.out.buffer("no prefs stated, will look for closest available")
        
        # feedsetsByDistance = sorted(feedsetsWithDistance, key=lambda deets: deets.distance)
        # feedsetsByNumSlots = sorted(feedsetsWithDistance, key=lambda deets: deets.numSlots)
        # go over the available sets, in order, and return
        # anything that is currently empty
        leastWastefulFreeSet = None 
        leastWasteValue = 1e6 # something gynormous
        for feedSelDeets in feedSetsByPriority:
            fs = feedSelDeets.feedSet
            if fs.numEntriesReserved() == 0:
                # is free
                wastedSpace = feedSelDeets.spaceWasted()
                if  wastedSpace < leastWasteValue:
                    leastWasteValue = wastedSpace
                    leastWastefulFreeSet = fs
        
        
        if leastWastefulFreeSet:
            # a completely free feedset!
            self.outputFSSearchDebug('EMPTY/least waste', projPart, feedSetsByPriority[0])
            return leastWastefulFreeSet 
        
        self.outputFSSearchDebug('No empties', projPart, feedSetsByPriority[0])
        # none were completely free of reservations, just return closest.
        return feedSetsByPriority[0].feedSet
    
    
    def mapPartToSplitFeedsets(self, projPart, totalQty):
        '''
            mapPartToSplitFeedsets
            Part did not completely fit in any individual feedset,
            but we've allowed splitting into multiple.
            Attempt that.
        '''
        feedsetSelDetails = []
        tableCapacity = 0
        pkgDescription = projPart.package_description
        for feedSet in self.feed_sets.entries():
            feedsetCapacity = feedSet.holdsUpTo(pkgDescription)
            if feedsetCapacity:
                # ok, we can hold a certain number...
                # make not of different feedset sizes
                numPerFeed = feedSet.spacePerFeedFor(pkgDescription)
                numSlotsForCapacity = feedsetCapacity // numPerFeed
                feedsetSelDetails.append([
                    numSlotsForCapacity,
                    totalQty - feedsetCapacity, # left overs
                    feedsetCapacity,
                    feedSet.prefersPackage(projPart.package_description),
                    feedSet 
                ])
                
                tableCapacity += feedsetCapacity
            
        if tableCapacity < totalQty:
            psypnp.debug.out.flush("NO SPACE for %s (split)\n" % str(projPart))
            return 0
        
        # ok, in theory we have enough capacity
        
        feedSetsByPriority = sorted(feedsetSelDetails, 
                                    key = lambda x: (
                                                       x[1], # leftovers
                                                       x[0], # numslots 
                                                       not x[3] # preference
                                                       ))
        
        # psypnp.debug.out.flush(str(feedSetsByPriority))
        numPartsMapped = 0
        totalFeedsReserved = 0
        psypnp.debug.out.buffer("\nSplit over multi-feedsets: %s\n" % str(projPart))
        
        for aFeedSetInfo in feedSetsByPriority:
            numComponentsSetCanCarry = aFeedSetInfo[2] # give feedset everything it can handle
            targetFeedset = aFeedSetInfo[4]
            
            toReserve = totalQty - numPartsMapped
            if toReserve > numComponentsSetCanCarry:
                toReserve = numComponentsSetCanCarry
            
            psypnp.debug.out.buffer("Split: trying to reserve %i in %s" % 
                                    (toReserve, targetFeedset))
            numFeedsReserved = self.mapPartToFeedset(targetFeedset, projPart, 
                                                     toReserve)
            if not numFeedsReserved:
                psypnp.debug.out.flush("SHOULDNT HAPPEN could not reserve split feed??")
            else:
                psypnp.debug.out.flush("(split) put %i into %s" % (toReserve, str(targetFeedset)))
                numPartsMapped += toReserve
                totalFeedsReserved += numFeedsReserved
                if numPartsMapped >= totalQty:
                    return totalFeedsReserved
        
        if numPartsMapped < totalQty:
            psypnp.debug.out.flush("NO SPACE: only mapped %i of %i %s" % (
                numPartsMapped,
                totalQty, 
                str(projPart)))
        
        return totalFeedsReserved
                
        
        
    def mapPartToFeedset(self, feedset, partToAssoc, totalQty):
        '''
            mapPartToFeedset
            the total qty of this part has been deemed to fit within a 
            certain number of slots of this feedset.
            Do the association.
        '''
        # have space! get the nearest available feed from this set
        num_associated = 0
        closestFeed = feedset.findNearestAvailableFeed()
        if closestFeed is None:
            psypnp.debug.out.flush("Have space but NO closest feed???")
            self.num_unplaced += 1
            return 0
        
        # now we'd like to reserve enough neighbouring feeds to hold 
        # a suitable number of strips for x boards
        numPerFeed = closestFeed.holdsUpTo(partToAssoc.package_description)
        if not numPerFeed:
            psypnp.debug.out.flush("No num/feed returned for part %s in %s" % (
                    partToAssoc,
                    closestFeed
                ))
            return 0
        # based on how many this feed can hold, we figure out total strips
        # needed
        numFeedsNeeded = math.ceil((1.0*totalQty)/numPerFeed)
        
        # now can getNeighbours() on the feed set, using our closest feed as 
        # the seed
        neighbourFeeds = feedset.getNeighbours(closestFeed, numFeedsNeeded)
        # that should be a list containing at least our "seed" feed, maybe more
        if neighbourFeeds and len(neighbourFeeds):
            # reserve them all by calling setPart on them
            for feedToReserve in neighbourFeeds:
                num_associated += 1
                psypnp.debug.out.buffer("Reserving feed %s for part %s" % (str(feedToReserve), 
                                                                           str(partToAssoc)))
                feedToReserve.setPart(partToAssoc, partToAssoc.package_description)
        
        return num_associated
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

        self.num_unplaced = 0
        
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
            if feedset is not None:
                # have space! get the nearest available feed from this set
                num_associated += self.mapPartToFeedset(feedset, apart, total_qty)
            else:
                # don't have space in single feed...
                if self.allow_part_spreading:
                    # but we can try split feeders
                    psypnp.debug.out.buffer("Split: No single feedset can hold %i of %s, trying spread\n" 
                                            % (total_qty, str(apart)))
                    
                    num_spread_slots = self.mapPartToSplitFeedsets(apart, total_qty)
                    
                    if num_spread_slots:
                        # success!  ok, done for this
                        num_associated += num_spread_slots
                    else:
                        psypnp.debug.out.flush("\n")
                        psypnp.debug.out.buffer("NO SPACE for %s\n" % str(apart))
                        self.num_unplaced += 1
                else: # no space and no part spreading... too bad.
                    psypnp.debug.out.flush("\n")
                    psypnp.debug.out.buffer("NO SPACE for %s\n" % str(apart))
                    self.num_unplaced += 1
            
            

        psypnp.debug.out.flush("Mapping is done.")
        return num_associated
    
    def compress(self):
        # get rid of empty spaces between occupied feeds
        self.feed_sets.compress()
        
    def apply(self):
        self.workspace.feeds.apply()
        
    
    def dump(self):
        self.workspace.feeds.dump()
        
    
    def __string__(self):
        return ' mapping "%s"' % (str(self.workspace.project))
    
    def __repr__(self):
        return '<WorkspaceMapper %s>' % self.__string__()
    
    
