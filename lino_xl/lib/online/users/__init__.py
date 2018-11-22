# Copyright 2015-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)
"""An extension of :mod:`lino.modlib.users` which adds functionality
for managing online registration.

.. autosummary::
   :toctree:

    models
    choicelists
    desktop

"""

from lino.modlib.users import Plugin


class Plugin(Plugin):
    needs_plugins = ['lino_xl.lib.countries']
    extends_models = ['User']
    online_registration = True
