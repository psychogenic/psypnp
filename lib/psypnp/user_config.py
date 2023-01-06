

# config feeders

# list any names of feeders to always leave untouched in reset part, e.g. permanent reels
feeders_reset_skiplist = [
    
    'ExampleReelLeft8mm_02',
    'ExampleReelLeft8mm_07'
    
    ] 


# auto-feed setup stuff
autofeedsetup_allow_part_spreading = True # allow a part to be spread amongst multiple feed sets
autofeedsetup_map_parts_to_preset_feeders = True # if a part is used in proj, and already mapped to feeder, leave it be 
autofeedsetup_leave_already_assoc_feeds_untouched = False # leave all non "fiducial" or "home" feeders untouched
autofeedsetup_restrict_to_enabled_feeders = False # only place in feeders that are enabled
