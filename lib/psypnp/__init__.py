'''
psypnp -- useful scripts for OpenPnP and support modules to roll your own


Released under the terms of the GPL v3 (see LICENSE file for details).

Have some imports here to smooth transition for older scripts.  You 
_should_ use the full path instead in new scripts (this may go away)

@see: https://inductive-kickback.com/2020/10/psypnp-for-openpnp/
@author: Pat Deegan
@copyright: Copyright (C) 2019-2020 Pat Deegan, https://psychogenic.com/
@license: GPL version 3, see LICENSE file for details.
'''

from .ui import (showError, showMessage, getOption, getUserInput)

from .util import (machine_is_running, should_proceed_with_motion)

