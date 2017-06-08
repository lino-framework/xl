# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""An extension of :mod:`lino.modlib.auth` which adds functionality
for managing online registration.

.. autosummary::
   :toctree:

    models
    choicelists
    desktop

"""

from lino.modlib.auth import Plugin


class Plugin(Plugin):
    needs_plugins = ['lino_xl.lib.countries']
    extends_models = ['User']
    online_registration = True
