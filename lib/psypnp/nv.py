'''
Non-Volatile storage.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/

Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.

This is a system for easy storage and retrieval of keys and 
dictionaries, on a per-script basis.

Simplest method: NVStorage objects.


 mystore = psypnp.nv.NVStorage('scriptname')
 if mystore.some_value is None:
     # never set
     mystore.some_value = 42 # default, now stored forevers

 if mystore.name == 'Bob':
     # didn't even check if it exists, 
     # it'll be None if it didn't
     print("Hi, bob")


Other more functiony functions provide for retrieval with 
defaults and such.

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

class NVStorage:
    '''
        NVStorage utility class.
        Just create with the parent key:
        mydata = NVStorage('scriptmasterkey')
        
        mydata.whatever will be None if never set or
        whatever you did set by doing:
        
         mydata.whatever = 'hohoho'
        or 
         mydata.whatever = 1.4141
        etc.
        
        Special value:
          mydata.autosave 
        defaults to True and does the automagic saving.
        
        Setting to false is a good way to avoid 50 writes
        when saving a lot of data, but you'll have to saveAll()
        or set it back to True (and make some assignement) to 
        preserve the mods made.
        
    '''
    def __init__(self, storageKey, autosave=True):
        self.__dict__['_key'] = storageKey 
        self.__dict__['autosave'] = autosave 
        
    def load(self, name, defaultValue=None):
        return get_subvalue(self._key, name, defaultValue)
    
    def save(self, name, val):
        set_subvalue(self._key, name, val)
        
    def saveAll(self):
        save_storage()
        
    def __getattr__(self, name):
        if name in self.__dict__:
            return self.__dict__[name]
        
        if name.find('__') == 0:
            pDict = get(self.__dict__['_key'])
            if pDict is not None:
                if hasattr(pDict, name):
                    return getattr(pDict, name)
            
            if hasattr(self.__dict__, name):
                return getattr(self.__dict__, name)
            return None 
        
        return get_subvalue(self.__dict__['_key'], name)
    
    def __setattr__(self, name, val):
        if name == '_key' or name == 'autosave':
            self.__dict__[name] = val 
        else:
            set_subvalue(self.__dict__['_key'], name, val, 
                         self.__dict__['autosave'])
        


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

if __name__ == "__main__":
    import psypnp.repl
    v = psypnp.repl.getStandardEnvVars()
    v['t'] = NVStorage('testo2')
    psypnp.repl.runInterpreter(v)
