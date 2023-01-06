'''
Created on Oct 16, 2020

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''
import psypnp.repl
import psypnp.debug

class FeedInfo:
    def __init__(self, aFeed):
        self.feed = aFeed
        self.name = aFeed.getName()
        self.distance_from_centroid = 1000
        self.associated_part = None
        self.package_description = None
        self.feed_description = None
        self.associated_part_maxcapacity = 0
        self.leave_unmodified = False # do not overwrite part association
        
        
    def moveTo(self, otherFeedInfo):
        otherFeedInfo.associated_part = self.associated_part
        otherFeedInfo.package_description = self.package_description
        self.associated_part = None
        self.package_description = None
        
    def getName(self):
        return self.name 
    def associatedPackageName(self):
        if self.package_description is None:
            return ''
        
        #return 'faaaak'
        
        return self.package_description.name 
    
    def associatedPartValue(self):
        if self.associated_part is None:
            return ''
        
        return self.associated_part.getValue()
    
    def associatedPartQuantity(self):
        if self.associated_part is None:
            return 0
        
        return self.associated_part.quantity()
        
    
    def available(self):
        if self.leave_unmodified:
            return False
        return self.associated_part is None
    
    def isEnabled(self):
        return self.feed.isEnabled()
        
    def holdsUpTo(self, aPackageDesc):
        if self.feed_description is None:
            psypnp.debug.out.buffer('holdsUpTo() [%s] -- no feed desc??' % str(self))
            return 0
        
        return self.feed_description.holdsUpTo(aPackageDesc)
    
    def canCarry(self, aPackageDesc):
        if self.feed_description is None:
            psypnp.debug.out.buffer('canCarry()[%s]-- no feed desc??' % str(self))
            return False
        return self.feed_description.canCarry(aPackageDesc)
    
    
    
    def setPart(self, aPartInfo, packageDesc):
        self.associated_part = aPartInfo
        self.package_description = packageDesc
        self.associated_part_maxcapacity = self.holdsUpTo(packageDesc)
        
    def getCurrentMachineFeedAssociatedPart(self):
        return self.feed.getPart()
    def __string__(self):
        return '%s (%s @ %s)' % (self.name, self.feed, str(self.distance_from_centroid))
    
    
    def __repr__(self):
        return '<FeedInfo %s>' % self.__string__()
    

class FeedSet:
    
    def __init__(self, name):
        self.name = name
        self.feeds = []
        self.feed_by_name = dict()
        
        
    def findByName(self, feedname):
        if feedname in self.feed_by_name:
            return self.feed_by_name[feedname]
        
        return None
    
    def remove(self, feedObj):
        if feedObj.name in self.feed_by_name:
            del self.feed_by_name[feedObj.name] 
            newFeeds = []
            for f in self.feeds:
                if f.name == feedObj.name:
                    psypnp.debug.out.buffer("Removing feed %s" % feedObj.name)
                else:
                    newFeeds.append(f)
            
            self.feeds = newFeeds
    
    def packagesInsertedStats(self):
        pkgs = dict()
        pkg_counts = dict()
        
        for finfo in self.entries():
            if finfo.available() or finfo.package_description is None:
                continue
            
            if finfo.package_description.name in pkgs:
                # already associated
                pkg_counts[finfo.package_description.name] += 1
            else:
                pkg_counts[finfo.package_description.name] = 1
                pkgs[finfo.package_description.name] = finfo.package_description
        
        return dict(
            packages=list(pkgs.values()),
            counts=pkg_counts
            )

    def packagesInserted(self):
        stats = self.packagesInsertedStats()
        return stats['packages']
    
    def prefersPackage(self, aPackageDesc):
        #if we've got nothing, well go away
        if not self.feeds or not len(self.feeds):
            return False
        
        # if a 'sample' feed here can't actually carry
        # this package, we assume none can, and we 
        # certainly don't prefer this type
        if not self.feeds[0].canCarry(aPackageDesc):
            return False
        
        # get some stats on what's up
        stats = self.packagesInsertedStats()
        
        # no packages held, we're empty, we have no preference
        if not len(stats['packages']):
            return False
        
        # we are holding packages, but NOT this type...
        # guess we lean another way, no preference
        if aPackageDesc.name not in stats['counts']:
            return False
        
        # we are holding packages, including at least this 
        # type.
        # if we are ONLY holding 1 type of package, we really
        # love this type, much preference:
        if len(stats['packages']) == 1:
            return True
        
        # ok, we have a mix.  Only declare preference if this type
        # of package is in the majority.
        max_count = 0
        target_count = 0
        for pd in stats['counts']:
            cur_count = stats['counts'][pd]
            if pd == aPackageDesc.name:
                target_count = cur_count
                
            if cur_count > max_count:
                max_count = cur_count
                
        
        return target_count >= max_count
            
        
    
    
            
    
    def getNeighbours(self, feedinfo, numNeeded):
        if numNeeded <= 1:
            return [feedinfo]
        
        feedNames = sorted(list(self.feed_by_name.keys()))
        seedFeedIndex = feedNames.index(feedinfo.name)

        psypnp.debug.out.buffer("Getting neighbours for feed")
        while seedFeedIndex > 0 and (seedFeedIndex + numNeeded) > len(feedNames):
            psypnp.debug.out.buffer("backup!")
            seedFeedIndex -= 1
        
        if seedFeedIndex < 0:
            psypnp.debug.out.flush("Uhm, seed feed index too small, what the hell?")
            return [feedinfo]
        
        retList = []
        
        endIdx = seedFeedIndex + numNeeded + 1
        i = seedFeedIndex
        # range() is a bitch
        numAdded = 0
        last_index_added = 0
        while i < endIdx and i < len(feedNames):
            fname = feedNames[i]
            
                
            if fname in self.feed_by_name and self.feed_by_name[fname].available():
                # psypnp.debug.out.flush("Found neighbour %s" % fname)
                retList.append(self.feed_by_name[fname])
                numAdded += 1
                last_index_added = i
                
            
            i += 1
        
        if numAdded >= numNeeded:
            psypnp.debug.out.buffer("Have all needed")
        else:
            psypnp.debug.out.buffer("need to add a few more")
            i = last_index_added
            while i >= 0 and  i<len(feedNames) and numAdded < numNeeded:
                if self.feed_by_name[feedNames[i]].available():
                    psypnp.debug.out.buffer("Adding %s" % feedNames[i])
                    retList.append(self.feed_by_name[feedNames[i]])
                    numAdded += 1
                i -= 1
            
        psypnp.debug.out.flush("Returning neighbours")
        psypnp.debug.out.clearAllCrumbs()
            
        return retList
    
    def spacePerFeedFor(self, ofPackage):
        # note: assumes all feeds in set are same size
        for finfo in self.feeds:
            if not finfo.available():
                continue 
            if finfo.feed_description is None:
                continue 
            can_hold = finfo.holdsUpTo(ofPackage)
            if can_hold > 0:
                return can_hold 
        
        return 0
    
    
    def holdsUpTo(self, ofPackage):
        total = 0
        for finfo in self.feeds:
            if not finfo.available():
                continue 
            if not finfo.canCarry(ofPackage):
                continue
            can_hold = finfo.holdsUpTo(ofPackage)
            
            if can_hold > 0:
                #psypnp.debug.out.buffer('feed %s says can hold %i' 
                #                        % (str(finfo), can_hold))
                total += can_hold 
        
        return total
        
    
    def numFeedsFor(self, numunits, ofPackage):
        '''
            numFeedsFor will return either:
              * the number of feeds it will eat up if it 
                CAN carry ALL numunits; or
              * 0/false
        '''
        space_needed = numunits
        num_feeds_required = 0
        for finfo in self.feeds:
            if not finfo.available():
                continue 
            if finfo.feed_description is None:
                continue 
            can_hold = finfo.holdsUpTo(ofPackage)
            if can_hold > 0:
                num_feeds_required += 1
                space_needed -= can_hold 
                if space_needed <= 0:
                    return num_feeds_required
        
        return 0 
            
    def findNearestAvailableFeed(self, restrictToEnabledFeeds=False):
        # psypnp.debug.out.buffer("findNearestAvailableFeed for %s..." % str(self))
        min_dist_feed = None
        for finfo in self.feeds:
            if finfo.available() and ((not restrictToEnabledFeeds) or finfo.isEnabled()):
                #psypnp.debug.out.buffer("%s avail!" % finfo.name)
                if min_dist_feed is None or finfo.distance_from_centroid < min_dist_feed.distance_from_centroid:
                    min_dist_feed = finfo
                
        
        
        return min_dist_feed
        
    def _nextFeedInUse(self, startingAt):
        
        i = startingAt + 1
        while i < self.numEntries():
            if not self.feeds[i].available():
                # this may be it
                if not self.feeds[i].leave_unmodified:
                    return self.feeds[i]
            i += 1
        
        return None 
    
    def compress(self):
        psypnp.debug.out.buffer("Compressing feedset %s" % self.name)
        if not self.numEntriesReserved():
            psypnp.debug.out.flush("but nothing here.")
            return 
        
        if not self.numEntriesAvailable():
            psypnp.debug.out.flush("but is full.")
            return 
        
        # we have some reserved and some available.
        i = 0
        while i<self.numEntries():
            if not self.feeds[i].available():
                i += 1
                continue 
            # feed i is available... find next in use
            nextFeedInUse = self._nextFeedInUse(i)
            if nextFeedInUse is not None:
                psypnp.debug.out.buffer("Moving feed into slot %i" % i)
                nextFeedInUse.moveTo(self.feeds[i])
            
            i += 1
            
        psypnp.debug.out.flush("Feedset compressed")
        
    def append(self, aFeed):
        finfo = FeedInfo(aFeed)
        self.feed_by_name[finfo.name] = finfo
        self.feeds.append(finfo)
        
    def entries(self):
        return sorted(self.feeds, key=lambda finfo: finfo.name)
    
    def numEntries(self):
        return len(self.feeds)
    
    def numEntriesAvailable(self):
        num_avail = 0
        for finfo in self.feeds:
            if finfo.available():
                num_avail += 1
                
        return num_avail
        
    
    def numEntriesReserved(self):
        num_res = 0
        for finfo in self.feeds:
            if not finfo.available():
                num_res += 1
                
        return num_res

    def __string__(self):
        return '%s (%i)' % (self.name, self.numEntries())
    
    
    def __repr__(self):
        return '<FeedSet %s>' % self.__string__()
    
    
class SystemFeeds:
    ''' 
        container for all the feed sets.
    '''
    def __init__(self):
        self.feedsets = dict()
        
        
    def get(self, name):
        if name in self.feedsets:
            return self.feedsets[name]
        return None
    
    def findFeedSetFor(self, feedname):
        '''
            to setup and check feed/metadata
        '''
        for fsname in self.feedsets:
            feedInfo = self.feedsets[fsname].findByName(feedname)
            if feedInfo is not None:
                return self.feedsets[fsname]
        
        return None
    
    def findSetWithSpaceFor(self, numunits, ofPackage):
        for fsname in self.feedsets:
            if self.feedsets[fsname].numFeedsFor(numunits, ofPackage):
                return self.feedsets[fsname]
            
        return None
    
    
    def compress(self):
        for fsname in self.feedsets:
            self.feedsets[fsname].compress()
            
    def append(self, aFeedSet):
        self.feedsets[aFeedSet.name] = aFeedSet
        
    def entries(self):
        return self.feedsets.values()
        
    def numEntries(self):
        return len(self.feedsets)
    

    def __string__(self):
        return 'SystemFeeds (%i)' % (self   .numEntries())
    
    
    def __repr__(self):
        return '<%s>' % self.__string__()




    
if __name__ == "__main__":
    # debugging assist... just run this module on command line
    
    v = psypnp.repl.getStandardEnvVars()
    v['SystemFeeds'] = SystemFeeds
    v['FeedSet'] = FeedSet
    
    psypnp.repl.runInterpreter(v)
        
    
    

