'''

Perform a check of feeder heights by lowering down nozzle to each,
in turn, allowing you to validate and/or modify feeder level.


@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

############## BOILER PLATE #################
# submitUiMachineTask should be used for all code that interacts
# with the machine. It guarantees that operations happen in the
# correct order, and that the user is presented with a dialog
# if there is an error.
from org.openpnp.util.UiUtils import submitUiMachineTask
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


from org.openpnp.model import Location, Length, LengthUnit 
from org.openpnp.util import MovableUtils

import psypnp
import psypnp.nv # non-volatile storage
import psypnp.search

MinSaneHeightAbs = 5.0
DoSubtractPartHeightFromLevel = False


StorageParentName = 'chkfeedht'

def main():
    keepLoopingUntilDone()
    
def keepLoopingUntilDone():
    shouldContinue = True
    while shouldContinue:
        shouldContinue = main_selection()

def main_selection():
    curIdx = get_current_idx()
    if curIdx < 0:
        curIdx = 0
 
    nextFeeder = get_next_feeder_from(curIdx)
    
    if nextFeeder is None:
        set_current_idx(0)
        return False

    sel = psypnp.getOption("Check Feeder Height", "Check feeder for \n%s \n%s " % 
                (nextFeeder.getName(), str(nextFeeder.getPart().getId())),
                ['Do it', 'Skip it', 'Find Feed', 'Find Part', 'Reset Count', 'Close'])

        
    if sel is None:
        # hard abort
        return False

    if sel == 0 and psypnp.should_proceed_with_motion():
        # do it
        return check_feeder_heights()
    if sel == 1: # skip it
        increment_idx_counter(curIdx)
        return True
    if sel == 2: # by name
        return set_idx_by_feedname()
    if sel == 3: # by part
        return set_idx_by_part()
    if sel == 4: # reset count
        reset_idx_counter()
        return True

    return False

def reset_idx_counter():
    psypnp.nv.set_subvalue(StorageParentName, 'curidx', 0)

def set_idx_by_part():
    # be nice and keep track of last search
    lastPartNameSearchVal = psypnp.nv.get_subvalue(StorageParentName, 'partsrch')
    if lastPartNameSearchVal is None:
        lastPartNameSearchVal = '100k'

    # ask for part name/id
    pname = psypnp.getUserInput("Name of part, or substring thereof", lastPartNameSearchVal)
    if pname is None or not len(pname):
        return False
    # store it for next time
    psypnp.nv.set_subvalue(StorageParentName, 'partsrch', pname)
    partsOfInterest =  psypnp.search.parts_by_name(pname)
    
    if partsOfInterest is None or not len(partsOfInterest):
        psypnp.ui.showError("No parts found for '%s'" % pname)
        return True
    
    allFeeds = get_sorted_feeders_list()
    if allFeeds is None or not len(allFeeds):
        psypnp.ui.showError("No feeders found at all?")
        return False
        
    
    matchingFeeds = psypnp.search.feeds_by_partslist(partsOfInterest, onlyEnabled=True, feederList=allFeeds) 
    if matchingFeeds is None or not len(matchingFeeds):
        psypnp.ui.showError("No feeders found for this part")
        return True
    
    if not _set_idx_to_feedid(matchingFeeds[0].getId(), allFeeds):
        psypnp.ui.showError("Weirdness -- could not extract feed idx??")
        
    return True


def _set_idx_to_feedid(feedId, allFeeds=None):
    if allFeeds is None:
        allFeeds = get_sorted_feeders_list()
        
    
    i = 0
    while i<len(allFeeds):
        if allFeeds[i].getId() == feedId:
            set_current_idx(i) 
            return True 
        i += 1
        
    return False 


def set_idx_by_feedname():
    # be nice and keep track of last search
    lastFeedNameSearchVal = psypnp.nv.get_subvalue(StorageParentName, 'feedsrch')
    if lastFeedNameSearchVal is None:
        lastFeedNameSearchVal = '8mmTop'

    # ask for part name/id
    feedname = psypnp.getUserInput("Name of feed, or substring thereof", lastFeedNameSearchVal)
    if feedname is None or not len(feedname):
        return False
    # store it for next time
    psypnp.nv.set_subvalue(StorageParentName, 'feedsrch', feedname)
    
    print("Searching for feed '%s'" % feedname)
    foundFeed = psypnp.search.feed_by_name(feedname)
    if foundFeed is not None:
        #print("Setting feed idx to %i" % feedDeets.index)
        if not _set_idx_to_feedid(foundFeed.getId()):
            psypnp.ui.showError("Couldn't set feed idx??")
        # set_current_idx(feedDeets.index)
    else:
        psypnp.ui.showError("Couldn't locate a feed \nmatching '%s'" % feedname)


    return True

def set_current_idx(valToSet):
    psypnp.nv.set_subvalue(StorageParentName, 'curidx', valToSet)


def increment_idx_counter(curIdx):
    nxtIdx = get_next_feeder_index(curIdx + 1)
    if nxtIdx is None:
        print("Out of feeders")
        # try from 0
        nxtIdx = get_next_feeder_index(0)
        if nxtIdx is None:
            nxtIdx = 0
        
        set_current_idx(nxtIdx)
    else:
        set_current_idx(nxtIdx)

def get_current_idx():
    cur_feeder_index = psypnp.nv.get_subvalue(StorageParentName, 'curidx')
    if cur_feeder_index is None:
        cur_feeder_index = 0

    return cur_feeder_index


def get_next_feeder_index(startidx):
    nxtFeed = None
    feederList = get_sorted_feeders_list()
    if feederList is None or not len(feederList):
        return 0

    next_feeder_index = startidx
    if next_feeder_index >= len(feederList):
        return 0

    foundNextFeeder = False
    while next_feeder_index < len(feederList) and not foundNextFeeder:
        nxtFeed = feederList[next_feeder_index]
        if not nxtFeed.isEnabled():
            next_feeder_index += 1
        else:
            # it is enabled, this is our guy
            if nxtFeed.getPart() is None:
                next_feeder_index += 1
            else:
                print("RETURNING IDX: %i" % next_feeder_index)
                return next_feeder_index

    return None





# we'll cache this list
Sorted_Feeders_List = None 
def get_sorted_feeders_list():
    global Sorted_Feeders_List
    if Sorted_Feeders_List is not None:
        return Sorted_Feeders_List
    
    sorted_feeders = psypnp.search.get_sorted_feeders_list()
    Sorted_Feeders_List = []
    for aFeeder in sorted_feeders:
        if aFeeder.isEnabled():
            Sorted_Feeders_List.append(aFeeder)
            
    return Sorted_Feeders_List



def get_next_feeder_from(startidx):
    nxtFeed = None
    print("GETTING NEXT FEEDER STARTING AT IDX %i" % startidx)
    feederList = get_sorted_feeders_list()
    if feederList is None or not len(feederList):
        psypnp.ui.showError("no feeders to check")
        return None


    next_feeder_index = get_next_feeder_index(startidx)
    if next_feeder_index is None or next_feeder_index >= len(feederList):
        psypnp.ui.showError("out of feeders to check")
        return None
    while next_feeder_index < len(feederList):
        nxtFeed = feederList[next_feeder_index]
        if nxtFeed.isEnabled():
            return nxtFeed 
        else:
            next_feeder_index = get_next_feeder_index(next_feeder_index)
    
    return None


def get_current_feeder():
    
    cur_feeder_index = get_current_idx()
    feederList = get_sorted_feeders_list()
    if feederList is None or not len(feederList):
        psypnp.ui.showError("no feeders found")
        return None
    
    curFeed = feederList[cur_feeder_index]

    return curFeed


def check_feeder_heights():
    return check_feeder_heights_motion()
def check_feeder_heights_motion():
    global StorageParentName
    
    cur_feeder_index = get_current_idx()
    #next_feeder_index = get_next_feeder_index(cur_feeder_index)
    
    
    curFeed = get_current_feeder()
    if curFeed is None:
        return False 
    if not curFeed.isEnabled():
        # we may have a stale current index
        reset_idx_counter()
        psypnp.ui.showError("Stale feed index, have reset. Please go again.")
        return True 
    
    #curFeed = get_next_feeder_from(next_feeder_index)
    feederPart = curFeed.getPart()
    print("Will move to feeder %i\n%s     \nwith part   \n%s    " % 
            (cur_feeder_index, str(curFeed.getName()), str(feederPart.getId())))
    
    defHead = machine.defaultHead
    defNozz = defHead.getDefaultNozzle()
    # always safeZ
    defHead.moveToSafeZ()
    psypnp.globals.machineExecuteMotions()
    # we don't want to go straight to the cam location--first XY, 
    # then Z
    feedPickLoc = curFeed.getPickLocation()
    safeMoveLocation = Location(feedPickLoc.getUnits(), feedPickLoc.getX(), feedPickLoc.getY(), 0, 45);
    MovableUtils.moveToLocationAtSafeZ(defNozz, safeMoveLocation)

    psypnp.globals.machineExecuteMotions()
    
    #print("WOULD MOVE FIRST TO: %s" % str(safeMoveLocation))
    
    locDepthZ = feedPickLoc.getZ()
    if MinSaneHeightAbs > abs(locDepthZ):
        print("Something weird with this feed -- height is %s" % str(locDepthZ))
        psypnp.ui.showError("Feeder height is strange: %s" % curFeed.getId())
        return False
    
    # length "down" to bottom of feed pick location, e.g. -35.00
    locDepthZLength = Length(locDepthZ, feedPickLoc.getUnits())
    
    # height of part, this is how much above the bottom of the feed pick 
    # location openpnp will travel before picking up
    partHeight = feederPart.getHeight()
    
    actualDepthZTravelled = locDepthZLength
    if DoSubtractPartHeightFromLevel:
        print("Removing part height from travel depth")
        actualDepthZTravelled = locDepthZLength.add(partHeight)
    
    # target location "real" depth openpnp will travel (as Location object)
    locRealDepth = Location(feedPickLoc.getUnits(), 0, 0, actualDepthZTravelled.getValue(), 0)
    
    # safe depth to travel to, basically real location depth + MinSaneHeightAbs (mm)
    locSafeDepth = locRealDepth.add(Location(LengthUnit.Millimeters, 0, 0, MinSaneHeightAbs, 45))
    
    # our first stage move is the (x,y) "safe" location with safe motion down
    locDownFirstStage = safeMoveLocation.add(locSafeDepth)
    # go there now
    defNozz.moveTo(locDownFirstStage)
    
    psypnp.globals.machineExecuteMotions()
    
    #print("NOW MOVE TO: %s" % str(locDownFirstStage))
    
    # now lets slow down
    curSpeed = machine.getSpeed()
    machine.setSpeed(0.25)
    
    #locFinalApproach = safeMoveLocation.add(locRealDepth)
    #locFinalApproach = feedPickLoc.subtract(locRealDepth)Location(feedPickLoc.getUnits(), 0, 0, actualDepthZTravelled.getValue(), 0)
    locFinalApproach = Location(feedPickLoc.getUnits(), feedPickLoc.getX(), feedPickLoc.getY(), 
                                actualDepthZTravelled.getValue(), feedPickLoc.getRotation())
    
    
    #print("WILL FINALLY MOVE TO: %s" % str(locFinalApproach))
    #print("ORIG FEEDPICK LOC: %s" % str(feedPickLoc))
    defNozz.moveTo(locFinalApproach)
    
    psypnp.globals.machineExecuteMotions()
    machine.setSpeed(curSpeed)

    keepShowing = True
    while keepShowing:
        sel = psypnp.getOption("Result", "How does %s look?" % curFeed.getName(),
                ['Thrilled!', 'Set Height', 'Up 0.1', 'Down 0.1', 'Up 1', 'Down 1'])

        if sel is None:
            defHead.moveToSafeZ()
            psypnp.globals.machineExecuteMotions()
            return False
        keepShowing = False
    
        if sel == 0:
            # all good
            increment_idx_counter(cur_feeder_index)
            defHead.moveToSafeZ()
            psypnp.globals.machineExecuteMotions()
            return True
        if sel == 1:
            # calculate height based on this
            # take the part height and call the feeder that much lower
            nozLoc = defNozz.getLocation()
            nozHeight = Length(nozLoc.getZ(), nozLoc.getUnits())
            feederHeight = nozHeight
            if DoSubtractPartHeightFromLevel:
                print("Adding part height to travel depth")
                feederHeight = nozHeight.subtract(partHeight)
            # now get the reference hole location
            refHole = curFeed.getReferenceHoleLocation()
            # create a new hole without a Z
            newHole = Location(refHole.getUnits(), refHole.getX(), refHole.getY(), 0, refHole.getRotation())
            # finally, add the feederHeight we determined
            #newHeight = nozLoc.getZ()
            newZLoc = Location(feederHeight.getUnits(), 0, 0, feederHeight.getValue(), 0)
            
            newHole = newHole.add(newZLoc)
            
            #print("WILL Set ref hole for %s to %s" % (feederPart.getName(), str(newHole)))
            curFeed.setReferenceHoleLocation(newHole)
            defHead.moveToSafeZ()
            psypnp.globals.machineExecuteMotions()
            increment_idx_counter(cur_feeder_index)
            return True
        if sel == 2: # Up 0.1
            feedPickLoc = feedPickLoc.add(Location(LengthUnit.Millimeters, 0, 0, 0.1, 0))
            defNozz.moveTo(feedPickLoc)
            psypnp.globals.machineExecuteMotions(defNozz)
            
            
            keepShowing = True
        if sel == 3: # Down 0.1
            feedPickLoc = feedPickLoc.subtract(Location(LengthUnit.Millimeters, 0, 0, 0.1, 0))
            defNozz.moveTo(feedPickLoc)
            psypnp.globals.machineExecuteMotions(defNozz)
            keepShowing = True
        if sel == 4: # Up 1
            feedPickLoc = feedPickLoc.add(Location(LengthUnit.Millimeters, 0, 0, 1, 0))
            defNozz.moveTo(feedPickLoc)
            psypnp.globals.machineExecuteMotions(defNozz)
            keepShowing = True
        if sel == 5: # Down 1
            feedPickLoc = feedPickLoc.subtract(Location(LengthUnit.Millimeters, 0, 0, 1, 0))
            defNozz.moveTo(feedPickLoc)
            psypnp.globals.machineExecuteMotions(defNozz)
            keepShowing = True

    
    return False


main()
