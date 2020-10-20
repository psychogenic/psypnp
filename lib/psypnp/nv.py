'''
Non-Volatile storage.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

This is a system for easy storage and retrieval of keys and 
dictionaries, on a per-script basis.

A global pickle file holds everything, scripts usually give 
themselves some relevant "parent key" (which maps to their 
own dict())

  MyKey = "somescript"

and then just get/set sub-values (which can be any simple
Python type... or anything that can be pickled):

  some_value = psypnp.nv.get_subvalue(MyKey, 'somename')
  if some_value is None:
      # was never set
      some_value = 3.14
      
  # later, to have access to this in future runs of script
  psypnp.nv.set_subvalue(MyKey, 'somename', some_value)



'''

import os
import pickle 

from psypnp.ui import showError
import psypnp.globals
import psypnp.config.files

PsyPersistentStorage = None
PsyNVStoreFileName = None 


def getStorageFileName():
    global PsyNVStoreFileName
    if PsyNVStoreFileName is not None:
        return PsyNVStoreFileName
    
    fpath = psypnp.globals.fullpathFromRelative(psypnp.config.files.NVStoreDb)
    if fpath and os.path.exists(fpath):
        PsyNVStoreFileName = fpath 
    
    return PsyNVStoreFileName    


def set_key(key, data, autoSave=True):
    st = load_storage()
    if st is None:
        return False
    st[key] = data
    if autoSave:
        save_storage()
    return True

def get(key):
    st = load_storage()
    if st is None or key not in st:
        return None

    return st[key]


def get_subvalue(parentname, key, defaultValue=None):
    st = load_storage()
    if st is None:
        return defaultValue
    if parentname not in st:
        st[parentname] = dict()
        return defaultValue
    if key not in st[parentname]:
        st[parentname][key] = defaultValue
        return defaultValue

    return st[parentname][key]

def set_subvalue(parentname, key, data, autoSave=True):
    st = load_storage()
    if st is None:
        return False
    if parentname not in st:
        st[parentname] = dict()
    st[parentname][key] = data
    if autoSave:
        save_storage()
    return True





def set_storage_filename(setto):
    global PsyNVStoreFileName
    if setto is not None and len(setto):
        PsyNVStoreFileName = setto
    else:
        showError("Gimme a name!")

def load_storage():
    global PsyPersistentStorage
    #print("ATTEMPT LOAD OF %s" % str(PsyNVStoreFileName))
    if PsyPersistentStorage is not None:
        #print("Already loaded, returning")
        return PsyPersistentStorage
    
    store_file = getStorageFileName()
    #print("XXXXXXXXXXXXXX opening %s" % store_file)
    if store_file and os.path.exists(store_file) and os.path.isfile(store_file):
        try:
            PsyPersistentStorage = pickle.load( open(store_file, "rb"))
            #print("Pickle loaded: %s" % str(PsyPersistentStorage))
        except Exception as ex:
            print("FAILED TO LOAD: %s" % str(ex))
            PsyPersistentStorage = dict()
    else:
        print("Seems %s DNE." % str(store_file))

    if PsyPersistentStorage is None:
        PsyPersistentStorage = dict()

    return PsyPersistentStorage

def save_storage(override=None):
    global PsyPersistentStorage
    if override is not None:
        PsyPersistentStorage = override

    store_file = getStorageFileName()
    if PsyPersistentStorage is None:
        showError("Nothing to save?")
        return
    #print("Pickle storage save")
    try:
        #print("DATA: %s" % str(PsyPersistentStorage))
        store_file = getStorageFileName()
        if store_file is None:
            showError("Storage file not set--globals setup??")
        
        #print("SAVING TO  %s" % str(store_file))
        fh = open(store_file, "wb")
        if fh is None:
            showError("Could not open: %s ?" % str(store_file))
            
        pickle.dump(PsyPersistentStorage, fh)
        fh.close()
        #print("Done save")
    except Exception as ex:
        showError("Problem serializing data: %s" % str(ex))
        return

