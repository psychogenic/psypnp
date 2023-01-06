'''
Created on Oct 17, 2020

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''
import psypnp.debug

import psypnp.auto.feed

from org.openpnp.model import Location
from org.openpnp.machine.reference.feeder import ReferenceStripFeeder

class FeedSwapper:
    def __init__(self):
        pass
    
    def movePart(self, fromOpnpFeed, toOpnpFeed, doSwap=True):
        
        srcFeed = fromOpnpFeed
        destFeed = toOpnpFeed
        
        srcPart = srcFeed.getPart()
        
        dstPart = destFeed.getPart()
        dstTape = destFeed.getTapeType()
        dstEnabled = destFeed.isEnabled()
        dstFeedCount = destFeed.getFeedCount()
        
        destFeed.setTapeType(srcFeed.getTapeType())
        if srcPart is None:
            destFeed.setEnabled(False)
        else:
            destFeed.setPart(srcPart)
            destFeed.setEnabled(srcFeed.isEnabled())
        
        destFeed.setFeedCount(srcFeed.getFeedCount())
        destFeed.setTapeType(srcFeed.getTapeType())
        
        if dstPart is None or not doSwap:
            srcFeed.setEnabled(False)
        else:
            srcFeed.setPart(dstPart)
            srcFeed.setEnabled(dstEnabled)
            srcFeed.setFeedCount(dstFeedCount)
            srcFeed.setTapeType(dstTape)
            
    
class FeedManager:
    
    def __init__(self):
        self.sets = psypnp.auto.feed.feed_sets()
        self.by_distance_list = psypnp.auto.feed.feeds_by_distance()
        self.num_feeds_processed = 0
        self.num_feeds_enabled = 0
        self.num_feeds_disabled = 0
        
        
    def resetFeedStats(self):
        self.num_feeds_processed = 0
        self.num_feeds_enabled = 0
        self.num_feeds_disabled = 0
        
        
    def numFeedsProcessed(self):
        return self.num_feeds_processed
    def numFeedsEnabled(self):
        return self.num_feeds_enabled
    def numFeedsDisabled(self):
        return self.num_feeds_disabled
    
    def apply(self):
        self.resetFeedStats()
        psypnp.debug.out.flush("Applying feed set changes... ")
        for feedset in self.sets.entries():
            psypnp.debug.out.flush("Handling feed set %s" % str(feedset))
            for finfo in feedset.entries():
                self.num_feeds_processed += 1
                psypnp.debug.out.buffer("Feed %s: " % str(finfo))
                
                if finfo.leave_unmodified:
                    psypnp.debug.out.flush('Feed will be left untouched')
                    continue
                
                opnpFeed = finfo.feed
                if finfo.available():
                    psypnp.debug.out.flush("disabling")
                    self.num_feeds_disabled += 1
                    opnpFeed.setEnabled(False)
                    continue
                
                
                self.num_feeds_enabled += 1
                #enable feed
                psypnp.debug.out.buffer("enabling")
                opnpFeed.setEnabled(True)


                # set part
                opnpPart = finfo.associated_part.part
                
                
                
                psypnp.debug.out.buffer("setting part to %s" % str(opnpPart))
                opnpFeed.setPart(opnpPart)
                if hasattr(opnpFeed, 'setMaxFeedCount'):
                    opnpFeed.setMaxFeedCount(finfo.associated_part_maxcapacity)
                    psypnp.debug.out.buffer("Reset feed count to 0")
                    opnpFeed.setFeedCount(0)
                
                # reset rotation
                
                psypnp.debug.out.buffer("zeroing rotation")
                if hasattr(opnpFeed, 'setLocation'):
                    oldLoc = opnpFeed.getLocation()
                    newLocation = Location(oldLoc.getUnits(), 
                                           oldLoc.getX(),
                                           oldLoc.getY(),
                                           oldLoc.getZ(),
                                           0.0)
                    opnpFeed.setLocation(newLocation)
                
                
                
                # set tape type for feed, if we can
                psypnp.debug.out.buffer("TapeType... ", False)
                if finfo.associated_part.package_description is not None \
                    and finfo.associated_part.package_description.tapetype:
                    
                    if hasattr(opnpFeed, 'setTapeType'):
                        ttypeMap = dict(
                            white=ReferenceStripFeeder.TapeType.WhitePaper,
                            black=ReferenceStripFeeder.TapeType.BlackPlastic,
                            clear=ReferenceStripFeeder.TapeType.ClearPlastic
                            
                        )
                        ttype = finfo.associated_part.package_description.tapetype
                        if ttype in ttypeMap:
                            
                            psypnp.debug.out.buffer("setting tapetype to %s" % ttype)
                            opnpFeed.setTapeType(ttypeMap[ttype])
                        else:
                            psypnp.debug.out.buffer("Could not set tapetype to '%s' ?" % str(ttype))
                else:
                    psypnp.debug.out.buffer("No tapetype specified?  Skipping")
                    
                psypnp.debug.out.flush("Done with feed.")
                
            psypnp.debug.out.flush("Done applying to all feed sets.")
            
    def dump(self):
        psypnp.debug.out.buffer("\n\n")
        for feedset in self.sets.entries():
            psypnp.debug.out.flush("\n\n FEEDSET: %s\n" % feedset.name)
            for finfo in feedset.entries():
                if finfo.available():
                    psypnp.debug.out.flush("\t%s\tFREE" % (finfo.name))
                else:
                    if finfo.leave_unmodified:
                        
                        psypnp.debug.out.flush("\t%s\t[UNTOUCHED] %s (%i/board)\t@%s\n" % 
                                            (finfo.name,
                                            finfo.getCurrentMachineFeedAssociatedPart().getId(),
                                            finfo.associatedPartQuantity(),
                                             str(finfo.distance_from_centroid)))
                    else:
                        psypnp.debug.out.flush("\t%s\t[%s] %s (%i/board)\t@%s\n" % 
                                            (finfo.name,  finfo.associatedPackageName(),
                                            finfo.associatedPartValue(),
                                            finfo.associatedPartQuantity(),
                                             str(finfo.distance_from_centroid)))
            
            psypnp.debug.out.flush("\n\n")
            