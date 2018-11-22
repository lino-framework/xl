# Copyright 2014-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Functionality for uploading files to the server and managing them.
This is an extension of :mod:`lino.modlib.uploads`.

It currently works only when you also have coaching installed, but
that dependency should not be very difficult to remove.

.. autosummary::
   :toctree:

    models
    fixtures.std
    fixtures.demo2

"""

from lino.modlib.uploads import Plugin


class Plugin(Plugin):

    extends_models = ['UploadType', 'Upload']

    # needs_plugins = ['lino_xl.lib.clients']

    def setup_main_menu(config, site, user_type, m):
        mg = site.plugins.office
        m = m.add_menu(mg.app_label, mg.verbose_name)
        m.add_action('uploads.MyExpiringUploads')
        m.add_action('uploads.MyUploads')
