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
import psypnp.ui

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

def feeds_by_partname(pname, onlyEnabled=True):
    
    
    #machine = psypnp.globals.machine()
    #config = psypnp.globals.config()
    matchingParts = parts_by_name(pname)
    if not len(matchingParts):
        showError("No parts matching name found")
        return None
    
    if len(matchingParts) > 1:
        print("Multiple matching parts, will select first match")

    return feeds_by_partslist(matchingParts, onlyEnabled)

def feeds_by_part(singlePartObj, onlyEnabled=True, 
                 returnAllMatching=False, 
                 feederList=None):
    ''' 
        feed_by_part PARTOBJ [onlyEnabled] [returnAllMatching] [feederList] 
        @param PARTOBJ: the part in question
        @param onlyEnabled:  only consider enabled feeders
        @param returnAllMatching: if False (default) returns only ONE feeder, first found
        @param feederList: search only within this list of feeders
        
        @return: A LIST of matching feeds or None if not found.
    '''
    if feederList is None:
        feederList = get_sorted_feeders_list()
        if feederList is None or not len(feederList):
            showError("No feeders found")
            return None 
    
    
    retList = []
    
    for aFeed in feederList: 
        if (onlyEnabled and aFeed.isEnabled()) or not onlyEnabled:
            feedPart =  aFeed.getPart()
            if feedPart.getId() == singlePartObj.getId():
                if returnAllMatching:
                    retList.append(aFeed) 
                else:
                    return [aFeed]
    
    
    if not len(retList):
        return None 
    
    return retList 



def feeds_by_partslist(partsList, onlyEnabled=True, returnAllMatching=False, feederList=None):
    '''
        feeds_by_partslist [onlyEnabled] [returnAllMatching]
        @param: onlyEnabled only consider enabled feeds
        @param: returnAllMatching if False (default), only one matching feed per part returned.
        
        @return: a list of feeds, or None if none found.
    '''
    
    if feederList is None:
        feederList = get_sorted_feeders_list()
        
    #print("DONIG222 FEEDBYPART FOR %s" % str(machine))
    if feederList is None or not len(feederList):
        showError("No feeders found")
        return None
    
    retList = []
    for aPart in partsList:
        matchingFeeds = feeds_by_part(aPart, onlyEnabled, returnAllMatching, feederList)
        if matchingFeeds is not None:
            retList.extend(matchingFeeds)
    
    if not len(retList):
        return None 
    
    return retList

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
    #print("Returning sorted feeds list:\n%s" % str(sorted_feeders))
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
    #matchingFeed = None
    lowerName = fname.lower()
    while stillSearching:
        cur_idx = get_next_feeder_index(cur_idx, onlyEnabled)
        if cur_idx is None or cur_idx >= len(feederList):
            return None 
        
        aFeed = feederList[cur_idx]
        if aFeed.getName().lower().find(lowerName) >= 0:
            # gotcha
            if aFeed.isEnabled() or not onlyEnabled:
                #return FeedDetails(aFeed, cur_idx)
                return aFeed

        cur_idx += 1
        if cur_idx >= len(feederList):
            # we're at the end of the line
            stillSearching = False
            return None


class SearchFeedResults:
    
    def __init__(self, searchName, matchingFeeds):
        self.searched = searchName
        self.results = matchingFeeds
        

def prompt_for_feeders_by_name(promptstr, defaultName=None):
    '''
        Prompts user for a search string (defaultName,
        used as default, if provided).
        
        @return: SearchFeedResults object or None
        None returned on abort.
        SearchFeedResults provides both the searched-for
        term (.searched) and the results list (which may be empty
    '''
    machine = psypnp.globals.machine()
    if defaultName is None or not len(defaultName):
        defaultName = '8mmLeft' # some default value
    
    pname = psypnp.ui.getUserInput(promptstr, defaultName)
    if pname is None or not len(pname):
        return None
    
    matchingFeeders = []
    
    for afeeder in machine.getFeeders():
        if afeeder.getName().find(pname) >= 0:
            matchingFeeders.append(afeeder)
    
    if not len(matchingFeeders):
        return  SearchFeedResults(matchingFeeders, pname)
    
    sortedMatchingFeeders = sorted(matchingFeeders, 
                                   key=_feed_key)
    return SearchFeedResults(
        pname,
        sortedMatchingFeeders)


