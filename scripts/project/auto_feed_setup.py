'''

Take a BOM and convert it to a skeleton config for your feeders.

This script is discussed in detail in the walk-through:
https://www.youtube.com/watch?v=pr9m46Z9CLA&list=PLWm3YS7ce87lW6aZhfV8zkwt3KYxqN-6R

To use, see the videos and/or my web page, but in short:
  1) Have strip feeders setup and named in a sane way, e.g.
     "8mmLeft_01, 8mmLeft_02..." and 
     "12mmTop_01, 12mmTop_02..." etc
     
  2) Adjust the feed_desc.csv and package_desc.csv in data/ directory
  
  3) prepare a BOM of suitable format. kicad supported natively, but:
    # Item(IGNORED),Qty,Reference(s),Value,LibPart(IGNORED),Footprint,...
    will do
  4) create your openpnp project and its board and import the placement/
     position file, so as to ensure all parts are created and available
     
  5) run this script and answer the questions
     
    
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

'''

############## BOILER PLATE #################
# boiler plate to get access to psypnp modules, outside scripts/ dir
import os.path
import sys
import traceback
python_scripts_folder = os.path.join(scripting.getScriptsDirectory().toString(),
                                      '..', 'lib')
sys.path.append(python_scripts_folder)

# setup globals for modules
import psypnp.globals
psypnp.globals.setup(machine, config, scripting, gui)

############## /BOILER PLATE #################

import os 
import psypnp
import psypnp.config.storagekeys as keys
import psypnp.project.workspace
import psypnp.auto.workspace

# you probably need to add your own here, unless you use
# BOMParserKicad, which expects a CSV with:
#   Item, Qty, Reference(s), Value, LibPart, Footprint
from psypnp.project.bom_parsers import BOMParserKicad

SelectedBOMParserType = BOMParserKicad

ParentKey = keys.ProjectManager
FeedDescCSVKey = keys.FeedDescCSV
PackageDescCSVKey = keys.PackageDescCSV

LastBomKey = 'lastbom'
LastBatchNumKey = 'lastbatch'




def problemWithFile(relpath):
    fpath = os.path.exists(psypnp.globals.fullpathFromRelative(relpath))
    if not fpath:
        psypnp.ui.showError("Can't find feed description file %s " % fpath)
        return True
    
    return False

def auto_setup():
    feed_desc_csv = psypnp.nv.get_subvalue(ParentKey, FeedDescCSVKey)
    package_desc_csv = psypnp.nv.get_subvalue(ParentKey, PackageDescCSVKey)
   
    if feed_desc_csv is None or package_desc_csv is None:
        psypnp.ui.showError("Please run set_feed/set_package scripts first")
        return
    
    if problemWithFile(feed_desc_csv) or problemWithFile(package_desc_csv):
        return 
    
    last_bom_csv = psypnp.nv.get_subvalue(ParentKey, LastBomKey)
    if last_bom_csv is None:
        last_bom_csv = ''
        
    bom_csv = psypnp.ui.getUserInput("BOM to use", last_bom_csv)
    
    if bom_csv is None:
        return 
    
    psypnp.nv.set_subvalue(ParentKey, LastBomKey, bom_csv)
    
    if not os.path.exists(psypnp.globals.fullpathFromRelative(bom_csv)):
        psypnp.ui.showError("Can't find bom %s " % bom_csv)
        return 
    
    try:
        #Create a WORKSPACE that knows about our meta information
        wspace = psypnp.project.workspace.Workspace(
            psypnp.globals.fullpathFromRelative(package_desc_csv), 
            psypnp.globals.fullpathFromRelative(feed_desc_csv))
        
        if not wspace.feed_descriptions.isOK():
            psypnp.ui.showError("Feed descriptions CSV reports NOT ok")
            return 
            
            
        if not wspace.package_descriptions.isOK():
            psypnp.ui.showError("package descriptions CSV reports NOT ok")
            return 
            
    except:
        
        print(traceback.format_exc())
        psypnp.ui.showError("GAG!")
        return
    
    try:
        # Create a PROJECT based on BOM
        proj = psypnp.project.project.Project(bom_csv, SelectedBOMParserType)
    except Exception as e:
        psypnp.ui.showError("Failed loading project %s" % str(e))
        return
    
    print(str(proj.part_map))
    
    if not proj.isOK():
        if psypnp.ui.getConfirmation("Project unhappy", 
        "Project has only mapped %i out of %i parts. Proceed?" % (
                proj.numMapped(),
                proj.numInBOM()
            )):
            wspace.ignoreProjectOKStatus = True
        else:
            return 

    
    # Set the workspace to be working on this project
    wspace.setProject(proj)

    if not wspace.isReady():
        psypnp.ui.showError("Workspace not ready--unknown issue. ugh.")
        return 
    
    # Create an auto-mapper
    mapper = psypnp.auto.workspace.WorkspaceMapper(wspace)
    if not mapper.isReady():
        psypnp.ui.showError("Workspace ready but mapper unhappy?")
        return
    
    last_batch_num = psypnp.nv.get_subvalue(ParentKey, LastBatchNumKey)
    if last_batch_num is None:
        last_batch_num = 4
    num_boards = psypnp.ui.getUserInputInt("Number of boards per batch", last_batch_num)
    if num_boards is None:
        return 
    
    psypnp.nv.set_subvalue(ParentKey, LastBatchNumKey, num_boards)
    if num_boards < 1 or num_boards > 50:
        psypnp.ui.showError("Please set a number of boards between 1-50.")
        return
    
    
    
    try:
        num_associated = mapper.map(num_boards)
    except Exception as exc:
        num_associated = 0
        psypnp.ui.showError("Ugh: problem mapping... (ran out of feeders?) %s" % str(exc))
        print(traceback.format_exc())
        return


    if num_associated:
        mapper.compress()
        mapper.dump()
    else:
        psypnp.ui.showError("Mapper associated NO feeds?")
        return
    

    confPrompt = "Mapped project to %i feeds.  Apply changes?" % num_associated
    num_left_over = mapper.numUnassociated()
    if (num_left_over):
        confPrompt = "Mapped to %i feeds (%i left unplaced, see Log).  Apply?" % (num_associated, num_left_over)

    
    if not psypnp.ui.getConfirmation("Apply Configuration", confPrompt):
        return 
        
    mapper.apply()
    
    psypnp.ui.showMessage("Changes applied.  %i feeds enabled out of %i feeds processed"
                          % 
                          (wspace.feeds.numFeedsEnabled(), wspace.feeds.numFeedsProcessed()))
    

        
    
    
   

auto_setup()
   
   
