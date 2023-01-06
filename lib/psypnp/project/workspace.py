'''
Created on Oct 17, 2020

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''

import psypnp.csv_file
import psypnp.debug
from psypnp.project.feed_manager import FeedManager

class Workspace:
    
    def __init__(self, 
                 package_desc_filename, 
                 feed_desc_filename):
        self.feeds = FeedManager()
        
        self.package_descriptions = psypnp.csv_file.PackageDescCSV(package_desc_filename)
        self.feed_descriptions = psypnp.csv_file.FeedDescCSV(feed_desc_filename)
        
        self.csv_success = self.package_descriptions.isOK() and self.feed_descriptions.isOK()
        
        self.project = None
        self.ignoreProjectOKStatus = False
        
    
    def isReady(self):
        if not self.csv_success:
            psypnp.debug.out.flush("Bad CSVs")
            return False
        
        if self.project is None:
            psypnp.debug.out.flush("No project set")
            return False
            
        if not self.project.isOK() and not self.ignoreProjectOKStatus:
            psypnp.debug.out.flush("Project not OK")
            return False
        
        return True
    
    def _findFeedNameInMap(self, fname, feedDescNameMap):
        
        for feedDescName in feedDescNameMap:
            psypnp.debug.out.flush("CHECK FDESCNAME %s" % feedDescName)
            if fname.find(feedDescName) >= 0:
                return feedDescNameMap[feedDescName]
        
        return None
    def setProject(self, aProject):
        '''
            setProject(workspace.project.Project obj)
        '''
        self.project = aProject 
        if self.project is None:
            return 
        
        psypnp.debug.out.buffer("Project workspace setting project %s" % str(aProject))
        
        feedDescNameMap = dict()
        for feedDesc in self.feed_descriptions.entries():
            feedDescNameMap[feedDesc.name] = feedDesc
            
        psypnp.debug.out.flush(str(feedDescNameMap))
        
        feedDistMap = dict()
        for feed_dist_tuple in self.feeds.by_distance_list:
            feedDistMap[feed_dist_tuple[0].getName()] = dict(
                    dist=feed_dist_tuple[1],
                    feed=feed_dist_tuple[0]
                )
        
        for feedSet in self.feeds.sets.entries():
            toRemove = []
            for feedInfo in feedSet.entries():
                
                if feedInfo.name in feedDistMap:
                    feedInfo.distance_from_centroid = feedDistMap[feedInfo.name]['dist']
                
                feedDesc = self._findFeedNameInMap(feedInfo.name, feedDescNameMap)
                if feedDesc is None:
                    psypnp.debug.out.flush('Could not find description for feed %s' % feedInfo.name)
                    
                    toRemove.append([feedSet, feedInfo])
                else:
                    feedInfo.feed_description = feedDesc
                    
            if len(toRemove):
                for remTup in toRemove:
                    remTup[0].remove(remTup[1])
                        
                    
        
        packDescMap = dict()
        for packDesc in self.package_descriptions.entries():
            packDescMap[packDesc.name] = packDesc
        
        for apart in self.project.part_map.parts:
            pkg = apart.part.getPackage()
            if pkg is not None:
                pid = pkg.getId()
                for pdescname in packDescMap:
                    if pid.find(pdescname) >= 0:
                        apart.package_description = packDescMap[pdescname]
                        continue


