'''
psypnp.ui -- utility methods for interacting with users in scripts.

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/


Part of the psypnp OpenPnP scripting modules project
@author: Pat Deegan
@copyright: Copyright (C) 2020 Pat Deegan, https://psychogenic.com
@license: GPL version 3, see LICENSE file for details.
'''

try:
    import javax.swing.JOptionPane as optPane
except:
    # this is just for running outside of openpnp
    from psypnp.debug import stubOptPane as optPane 

import psypnp.globals

def showError(msg, title=None):
    print("ERROR: %s" % str(msg))
    optPane.showMessageDialog(None, msg)

def showMessage(msg, title=None):
    optPane.showMessageDialog(None, msg)


def getUserInput(msg, defaultValue=''):
    return optPane.showInputDialog(msg, defaultValue)

def getUserInputInt(msg, defaultValue=0):
    v = getUserInput(msg, str(defaultValue))
    if v is None:
        return None 
    try:
        v = int(v)
    except:
        return None 
    
    return v

def getUserInputFloat(msg, defaultValue=0):
    v = getUserInput(msg, str(defaultValue))
    if v is None:
        return None 
    try:
        v = float(v)
    except:
        return None 
    
    return v



def getOption(title, message, options, optDefault=None):
    if optDefault is None:
        optDefault = options[0]

    val = optPane.showOptionDialog(None, message, title,
                optPane.DEFAULT_OPTION, optPane.INFORMATION_MESSAGE, None, 
                options, optDefault);
    return val 


def getConfirmation(title, message, options=None, optDefault=None):
    ''' 
    @return: True if user says "yes" false otherwise.
    @note: Always set "YES" as second option.
    '''
    if options is None:
        options = ["Yes", "No"]
     
    if optDefault is None:   
        optDefault = options[0]
        
    val = getOption(title, message, options, optDefault)
    if val == 0:
        return True
    
    return False

def getSelectedBoards():
    boardLocs = psypnp.globals.gui().jobTab.getSelections()
    if not boardLocs or (not len(boardLocs)) or not boardLocs[0]:
        return None
    
    boardsList = []
    for bloc in boardLocs:
        boardsList.append(bloc.board)

    return boardsList

def getSelectedFeeders():
    feederSelections = psypnp.globals.gui().getFeedersTab().getSelections()
    
    feedersList = []
    for f in feederSelections:
        
        fname = f.toString()
        if fname and len(fname):
            fname = fname.replace('[', '')
            fname = fname.replace('[', '')
            feedersList.append(fname)
            
    return feedersList
        
