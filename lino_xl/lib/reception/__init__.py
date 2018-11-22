# -*- coding: UTF-8 -*-
# Copyright 2013-2016 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)

"""This module is for managing a reception desk and a waiting queue:
register clients into a waiting queue as they present themselves at a
reception desk (Empfangsschalter), and unregister them when they leave
again.

It depends on :mod:`lino_xl.lib.cal`. It does not add any model, but
adds some workflow states, actions and tables.

Extended by :mod:`lino_welfare.modlib.reception`.


.. autosummary::
   :toctree:

    models
    workflows


"""
from lino.api import ad, _


class Plugin(ad.Plugin):
    "See :class:`lino.core.Plugin`."
    verbose_name = _("Reception")

    needs_plugins = ['lino.modlib.system', 'lino_xl.lib.cal']

    required_user_groups = 'reception'
    """The required user groups for viewing actors of this plugin.
    
    This is overridden by Lino Welfare to include "coaching".

    This way of configuring permissions is an example for why it would
    be useful to replace user groups by a UserType class (and to
    populate UserTypes with subclasses of it).

    """

    def setup_main_menu(config, site, user_type, m):
        app = site.plugins.reception
        m = m.add_menu(app.app_name, app.verbose_name)

        m.add_action('cal.EntriesByDay')

        m.add_action('reception.WaitingVisitors')
        m.add_action('reception.BusyVisitors')
        m.add_action('reception.GoneVisitors')

        # MyWaitingVisitors is maybe not needed as a menu entry since it
        # is also a get_dashboard_items. if i remove it then i must edit
        # `pcsw_tests.py`.  Waiting for user feedback before doing this.
        m.add_action('reception.MyWaitingVisitors')

