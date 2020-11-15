'''
search: utility functions for searching for stuff (parts/feeders).

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''
from psypnp.ui import showError
import psypnp.globals 

def parts_by_name(pname):
    '''
        parts_by_name(PARTNAME:str)
        @return: a list of parts whos names contain the PARTNAME string.
    '''
    matchingParts = []
    config = psypnp.globals.config()
    partByName = config.getPart(pname)
    if partByName is not None:
        matchingParts.append(partByName)
    else:
        lowerName = pname.lower()
        for apart in config.getParts():
            if apart.id.lower().find(lowerName) >= 0:
                matchingParts.append(apart)
    return matchingParts


def parts_by_package(package):
    '''
        parts_by_package(PACKAGEOBJ)
        @return: a list of parts using package PACKAGEOBJ.
    '''
    srcPackId = package.getId()
    matchingParts = []
    config = psypnp.globals.config()
    for apart in config.getParts():
        pkg = apart.getPackage()
        if pkg is not None and pkg.getId() == srcPackId:
            matchingParts.append(apart)
    
    return matchingParts


def packages_by_name(pname):
    '''
        packages_by_name(PKGNAME:str)
        @return: a list of package objects whos name (id) contains PKGNAME
    '''
    config = psypnp.globals.config()
    matchingPackages = []
    pnameLower = pname.lower()
    for apkg in config.getPackages():
        pid = apkg.getId()
        if pid and len(pid):
            if pid.lower().find(pnameLower) >= 0:
                matchingPackages.append(apkg)
    
    return matchingPackages

def parts_by_package_name(pkgname):
    '''
        parts_by_package_name(PKGNAME:str)
        @return: a list of part objects who's package id contains PKGNAME
    '''
    matchingParts = []
    matchingPkgs = packages_by_name(pkgname)
    if not len(matchingPkgs):
        return matchingParts
    
    # could just use a bunch of calls to parts_by_package
    # but I just can't take the horrible inefficiency
    pkgsOfInterest = dict()
    for pkg in matchingPkgs:
        pkgsOfInterest[pkg.getId()] = pkg
    
    for apart in psypnp.globals.config().getParts():
        partPkg = apart.getPackage()
        if partPkg is not None and partPkg.getId() in pkgsOfInterest:
            matchingParts.append(apart)
            
    return matchingParts


def get_next_feeder_index(startidx, onlyEnabled=True):
    nxtFeed = None
    #machine = psypnp.globals.machine()
    feederList = get_sorted_feeders_list()
    if feederList is None or not len(feederList):
        return 0
    
    next_feeder_index = startidx
    if next_feeder_index >= len(feederList):
        return 0
    
    foundNextFeeder = False
    while next_feeder_index < len(feederList) and not foundNextFeeder:
        nxtFeed = feederList[next_feeder_index]
        if onlyEnabled and not nxtFeed.isEnabled():
            next_feeder_index += 1
        else:
            # it is enabled, this is our guy
            if nxtFeed.getPart() is None:
                # but there's no part associated, skip
                next_feeder_index += 1
            else:
                return next_feeder_index
    
    print("Could not find next feeder index")
    return 1001 # random large num


class FeedDetails:
    def __init__(self, feed, index):
        self.feed = feed
        self.index = index

def feed_by_partname(pname, onlyEnabled=True):
    
    
    #machine = psypnp.globals.machine()
    #config = psypnp.globals.config()
    matchingParts = parts_by_name(pname)
    if not len(matchingParts):
        showError("No parts matching name found")
        return None
    
    if len(matchingParts) > 1:
        print("Multiple matching parts, will select first match")

    return feed_by_parts(matchingParts, onlyEnabled)

def feed_by_parts(partsList, onlyEnabled=True):
    #print("DONIG FEEDBYPART FOR %s" % str(machine))
    
    #machine = psypnp.globals.machine()
    # get our feeders
    feederList = get_sorted_feeders_list()
    #print("DONIG222 FEEDBYPART FOR %s" % str(machine))
    if feederList is None or not len(feederList):
        showError("No feeders found")
        return None
    
    stillSearching = True
    cur_idx = 0
    matchingFeed = None
    while matchingFeed is None and stillSearching:
        cur_idx = get_next_feeder_index(cur_idx, 
                                        onlyEnabled)
        if cur_idx is None or cur_idx > len(feederList):
            return None 
        
        aFeed = feederList[cur_idx]
        feedPart =  aFeed.getPart()
        #print("Checking if feed %i is a match" % cur_idx)
        if feedPart is not None:
            for aPart in partsList:
                if aPart.id == feedPart.id:
                    matchingFeed = aFeed
                    stillSearching = False
                    break
            if not stillSearching:
                break

        cur_idx += 1
        if cur_idx >= len(feederList):
            # we're at the end of the line
            stillSearching = False

    if stillSearching or not matchingFeed:
        showError("Could not find any match for part(s)")
        return None
    
    return FeedDetails(matchingFeed, cur_idx)

def _feed_key(afeed):
    
    if afeed is None:
        return ''
    
    if hasattr(afeed, 'getName'):
        return afeed.getName()
    
    return afeed.getId()

def get_sorted_feeders_list():
    machine = psypnp.globals.machine()
    feeders = machine.getFeeders()
    
    sorted_feeders = sorted(feeders, key=_feed_key)
    print("Returning sorted feeds list:\n%s" % str(sorted_feeders))
    return sorted_feeders




def feed_by_name(fname, onlyEnabled=True):
    # get our feeders
    #machine = psypnp.globals.machine()
    feederList = get_sorted_feeders_list()
    if feederList is None or not len(feederList):
        showError("No feeders found")
        return None

    stillSearching = True
    cur_idx = 0
    matchingFeed = None
    lowerName = fname.lower()
    while stillSearching:
        cur_idx = get_next_feeder_index(cur_idx, onlyEnabled)
        if cur_idx is None or cur_idx >= len(feederList):
            return None 
        
        aFeed = feederList[cur_idx]
        if aFeed.getName().lower().find(lowerName) >= 0:
            # gotcha
            if aFeed.isEnabled() or not onlyEnabled:
                return FeedDetails(aFeed, cur_idx)

        cur_idx += 1
        if cur_idx >= len(feederList):
            # we're at the end of the line
            stillSearching = False
            return None

