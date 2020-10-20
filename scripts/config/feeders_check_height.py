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

    sel = psypnp.getOption("Check Feeder Height", "Check feeder for \n%s \n%s " % 
                (nextFeeder.getName(), str(nextFeeder.getPart().getId())),
                ['Do it', 'Skip it', 'Find Feed', 'Find Part', 'Reset Count', 'Close'])

        
    if sel is None:
        # hard abort
        return False

    if sel == 0 and psypnp.should_proceed_with_motion(machine):
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

    feedDeets = psypnp.feed_by_partname(pname)
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

    feedDeets = psypnp.feed_by_name(feedname)
    if feedDeets is not None and feedDeets:
        set_current_idx(feedDeets.index)
    else:
        psypnp.showError("Couldn't locate a feed \nmatching '%s'" % feedname)


    return True

def set_current_idx(valToSet):
    psypnp.nv.set_subvalue(StorageParentName, 'curidx', valToSet)

def increment_idx_counter(curIdx):
    set_current_idx(get_next_feeder_index(curIdx + 1))

def get_current_idx():
    cur_feeder_index = psypnp.nv.get_subvalue(StorageParentName, 'curidx')
    if cur_feeder_index is None:
        cur_feeder_index = 0

    return cur_feeder_index


def get_next_feeder_index(startidx):
    nxtFeed = None
    feederList = machine.getFeeders()
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

    return 1000 # random large num








def get_next_feeder_from(startidx):
    nxtFeed = None
    print("GETTING NEXT FEEDER STARTING AT IDX %i" % startidx)
    feederList = machine.getFeeders()
    if feederList is None or not len(feederList):
        psypnp.showError("no feeders to check")
        return None


    next_feeder_index = get_next_feeder_index(startidx)
    if next_feeder_index >= len(feederList):
        psypnp.showError("out of feeders to check")
        return None

    nxtFeed = feederList[next_feeder_index]

    return nxtFeed




def check_feeder_heights():
    global StorageParentName
    cur_feeder_index = get_current_idx()
    next_feeder_index = get_next_feeder_index(cur_feeder_index)
    nxtFeed = get_next_feeder_from(next_feeder_index)
    feederPart = nxtFeed.getPart()
    print("Will move to feeder %i\n%s     \nwith part   \n%s    " % 
            (next_feeder_index, str(nxtFeed.getName()), str(feederPart.getId())))

    # always safeZ
    machine.defaultHead.moveToSafeZ()
    # we don't want to go straight to the cam location--first XY, 
    # then Z
    feedPickLoc = nxtFeed.getPickLocation()
    safeMoveLocation = Location(feedPickLoc.getUnits(), feedPickLoc.getX(), feedPickLoc.getY(), 0, 45);
    machine.defaultHead.defaultNozzle.moveTo(safeMoveLocation)
    print("WOULD MOVE FIRST TO: %s" % str(safeMoveLocation))

    locRealDepth = Location(feedPickLoc.getUnits(), 0, 0, feedPickLoc.getZ(), 0)
    locSafeDepth = locRealDepth.add(Location(LengthUnit.Millimeters, 0, 0, 6, 0))
    locDownFirstStage = safeMoveLocation.add(locSafeDepth)
    machine.defaultHead.defaultNozzle.moveTo(locDownFirstStage)
    print("WOULD THEN MOVE TO: %s" % str(locDownFirstStage))
    curSpeed = machine.getSpeed()
    machine.setSpeed(0.25)
    print("WOULD FINALLY MOVE TO: %s" % str(feedPickLoc))
    machine.defaultHead.defaultNozzle.moveTo(feedPickLoc)
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
            increment_idx_counter(next_feeder_index)
            machine.defaultHead.moveToSafeZ()
            return True
        if sel == 1:
            # calculate height based on this
            # take the part height and call the feeder that much lower
            pHeight = feederPart.getHeight()
            nozLoc = machine.defaultHead.defaultNozzle.location
            nozHeight = Length(nozLoc.getZ(), nozLoc.getUnits())
            feederHeight = nozHeight.subtract(pHeight)
            # now get the reference hole loctation
            refHole = nxtFeed.getReferenceHoleLocation()
            # create a new hole without a Z
            newHole = Location(refHole.getUnits(), refHole.getX(), refHole.getY(), 0, refHole.getRotation())
            # finally, add the feederHeight we determined
            newZLoc = Location(feederHeight.getUnits(), 0, 0, nozLoc.getZ(), 0)
            newHole = newHole.add(newZLoc)
            print("WILL Set ref hole for %s to %s" % (feederPart.getName(), str(newHole)))
            nxtFeed.setReferenceHoleLocation(newHole)
            machine.defaultHead.moveToSafeZ()
            increment_idx_counter(next_feeder_index)
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
