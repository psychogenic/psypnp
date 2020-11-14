'''

Perform a check of feeder heights by lowering down nozzle to each,
in turn, allowing you to validate and/or modify feeder level.


@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

############## BOILER PLATE #################
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

import psypnp
import psypnp.nv # non-volatile storage
import psypnp.search

MinSaneHeightAbs = 5.0

StorageParentName = 'chkfeedht'

def main():
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

    feedDeets = psypnp.search.feed_by_partname(pname)
    if feedDeets is None or not feedDeets:
        return True

    set_current_idx(feedDeets.index)
    return True


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
    feedDeets = psypnp.search.feed_by_name(feedname)
    if feedDeets is not None and feedDeets:
        print("Setting feed idx to %i" % feedDeets.index)
        set_current_idx(feedDeets.index)
    else:
        psypnp.showError("Couldn't locate a feed \nmatching '%s'" % feedname)


    return True

def set_current_idx(valToSet):
    psypnp.nv.set_subvalue(StorageParentName, 'curidx', valToSet)


def increment_idx_counter(curIdx):
    nxtIdx = get_next_feeder_index(curIdx + 1)
    if nxtIdx is None:
        print("Out of feeders")
        set_current_idx(0)
    
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
    Sorted_Feeders_List = psypnp.search.get_sorted_feeders_list()
    return Sorted_Feeders_List



def get_next_feeder_from(startidx):
    nxtFeed = None
    print("GETTING NEXT FEEDER STARTING AT IDX %i" % startidx)
    feederList = get_sorted_feeders_list()
    if feederList is None or not len(feederList):
        psypnp.showError("no feeders to check")
        return None


    next_feeder_index = get_next_feeder_index(startidx)
    if next_feeder_index is None or next_feeder_index >= len(feederList):
        psypnp.showError("out of feeders to check")
        return None

    nxtFeed = feederList[next_feeder_index]

    return nxtFeed


def get_current_feeder():
    
    cur_feeder_index = get_current_idx()
    feederList = get_sorted_feeders_list()
    if feederList is None or not len(feederList):
        psypnp.showError("no feeders found")
        return None
    
    curFeed = feederList[cur_feeder_index]

    return curFeed


def check_feeder_heights():
    global StorageParentName
    
    cur_feeder_index = get_current_idx()
    #next_feeder_index = get_next_feeder_index(cur_feeder_index)
    
    
    curFeed = get_current_feeder()
    #curFeed = get_next_feeder_from(next_feeder_index)
    feederPart = curFeed.getPart()
    print("Will move to feeder %i\n%s     \nwith part   \n%s    " % 
            (cur_feeder_index, str(curFeed.getName()), str(feederPart.getId())))

    # always safeZ
    machine.defaultHead.moveToSafeZ()
    # we don't want to go straight to the cam location--first XY, 
    # then Z
    feedPickLoc = curFeed.getPickLocation()
    safeMoveLocation = Location(feedPickLoc.getUnits(), feedPickLoc.getX(), feedPickLoc.getY(), 0, 45);
    machine.defaultHead.defaultNozzle.moveTo(safeMoveLocation)
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
    
    actualDepthZTravelled = locDepthZLength.add(partHeight)
    
    # target location "real" depth openpnp will travel (as Location object)
    locRealDepth = Location(feedPickLoc.getUnits(), 0, 0, actualDepthZTravelled.getValue(), 0)
    
    # safe depth to travel to, basically real location depth + MinSaneHeightAbs (mm)
    locSafeDepth = locRealDepth.add(Location(LengthUnit.Millimeters, 0, 0, MinSaneHeightAbs, 45))
    
    # our first stage move is the (x,y) "safe" location with safe motion down
    locDownFirstStage = safeMoveLocation.add(locSafeDepth)
    # go there now
    machine.defaultHead.defaultNozzle.moveTo(locDownFirstStage)
    print("NOW MOVE TO: %s" % str(locDownFirstStage))
    
    # now lets slow down
    curSpeed = machine.getSpeed()
    machine.setSpeed(0.25)
    
    #locFinalApproach = safeMoveLocation.add(locRealDepth)
    #locFinalApproach = feedPickLoc.subtract(locRealDepth)Location(feedPickLoc.getUnits(), 0, 0, actualDepthZTravelled.getValue(), 0)
    locFinalApproach = Location(feedPickLoc.getUnits(), feedPickLoc.getX(), feedPickLoc.getY(), 
                                actualDepthZTravelled.getValue(), feedPickLoc.getRotation())
    
    
    print("WILL FINALLY MOVE TO: %s" % str(locFinalApproach))
    print("ORIG FEEDPICK LOC: %s" % str(feedPickLoc))
    machine.defaultHead.defaultNozzle.moveTo(locFinalApproach)
    machine.setSpeed(curSpeed)

    keepShowing = True
    while keepShowing:
        sel = psypnp.getOption("Result", "How does it look?",
                ['Thrilled!', 'Set Height', 'Up 0.1', 'Down 0.1', 'Up 1', 'Down 1'])

        if sel is None:
            machine.defaultHead.moveToSafeZ()
            return False
        keepShowing = False
    
        if sel == 0:
            # all good
            increment_idx_counter(cur_feeder_index)
            machine.defaultHead.moveToSafeZ()
            return True
        if sel == 1:
            # calculate height based on this
            # take the part height and call the feeder that much lower
            nozLoc = machine.defaultHead.defaultNozzle.location
            nozHeight = Length(nozLoc.getZ(), nozLoc.getUnits())
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
            machine.defaultHead.moveToSafeZ()
            increment_idx_counter(cur_feeder_index)
            return True
        if sel == 2: # Up 0.1
            feedPickLoc = feedPickLoc.add(Location(LengthUnit.Millimeters, 0, 0, 0.1, 0))
            machine.defaultHead.defaultNozzle.moveTo(feedPickLoc)
            keepShowing = True
        if sel == 3: # Down 0.1
            feedPickLoc = feedPickLoc.subtract(Location(LengthUnit.Millimeters, 0, 0, 0.1, 0))
            machine.defaultHead.defaultNozzle.moveTo(feedPickLoc)
            keepShowing = True
        if sel == 4: # Up 1
            feedPickLoc = feedPickLoc.add(Location(LengthUnit.Millimeters, 0, 0, 1, 0))
            machine.defaultHead.defaultNozzle.moveTo(feedPickLoc)
            keepShowing = True
        if sel == 5: # Down 1
            feedPickLoc = feedPickLoc.subtract(Location(LengthUnit.Millimeters, 0, 0, 1, 0))
            machine.defaultHead.defaultNozzle.moveTo(feedPickLoc)
            keepShowing = True

    
    return False


main()
