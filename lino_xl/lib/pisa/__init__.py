# Copyright 2014-2016 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Deprecated. We recommend to use :mod:`lino_xl.lib.appypod`
instead.

This plugin installs a button to "print" any table into PDf using
Pisa.

To use it, simply add the following line to your
:meth:`lino.core.site.Site.get_installed_apps`::

    yield 'lino_xl.lib.pisa'

"""

from lino import ad

from django.utils.translation import gettext_lazy as _


class Plugin(ad.Plugin):
    "See :doc:`/dev/plugins`."
    verbose_name = _("Print table using Pisa")

