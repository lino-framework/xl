# Copyright 2015-2017 Luc Saffre
# License: BSD (see file COPYING for details)
"""
Adds online registration feature to :mod:`lino.modlib.users`.

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
