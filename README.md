# psypnp

psypnp -- useful scripts for [OpenPnP](https://openpnp.org/) and a library of Python support modules to roll your own

Copyright (C) 2019-2020 Pat Deegan, [https://psychogenic.com/](https://psychogenic.com/)

Released under the terms of the *GPL v3* (see LICENSE file for details).

[psypnp project](https://inductive-kickback.com/2020/10/psypnp-for-openpnp/)

# Overview

This package comes with two sets of components:

  * some [utility scripts](https://inductive-kickback.com/2020/10/psypnp-for-openpnp/#scripts) to control an OpenPnP pick & place machine
  * a set of [Python modules](https://inductive-kickback.com/2020/10/psypnp-for-openpnp/#psypnp-modules) that are used by the above scripts that can help you write powerful scripts of your own, easily

The scripts include various motion control, configuration scripts that save me tons of clicking, a visualizer that shows you feed arrangement graphically through a generated SVG image, a useful REPL terminal, and more.

The modules have facilities for non-volatile information storage, easy use of the GUI to query users and other useful things.

See: [psypnp for OpenPnP](https://inductive-kickback.com/2020/10/psypnp-for-openpnp/) for a complete description and usage guide.

# Installation
The contents of this project are meant to be house under the OpenPnP configuration directory (the place where it looks for the scripts/ directory for the contents of the Scripts toolbar menu).


Scripts, to be visible to OpenPnP, must be in the proper directory (~/.openpnp2/scripts under Linux).  

Installation is as simple as sticking the contents of:
 scripts/
 data/
and
 lib/

in there with the rest of the OpenPnP configuration.  

The data/ dir is used to hold the non-volatile "db" (pickle) with information we want to have access to between script runs, so must be writeable by the OpenPnP process. 

# Usage

The scripts themselves, once installed, will be found under the OpenPnP Scripts menu. See the [project description page](https://inductive-kickback.com/2020/10/psypnp-for-openpnp/) or the source for details, but many of them are pretty self-explanatory.

Same story for the modules.  There are [examples online](https://inductive-kickback.com/2020/10/psypnp-for-openpnp/#psypnp-modules) and in the scripts, but I also have an [OpenPnP Scripting Deep Dive series on Youtube](https://www.youtube.com/watch?v=pr9m46Z9CLA&list=PLWm3YS7ce87lW6aZhfV8zkwt3KYxqN-6R)
that may be of interest.


