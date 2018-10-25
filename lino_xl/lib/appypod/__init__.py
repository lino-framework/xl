# Copyright 2014-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""
Adds functionality for generating printable documents using
LibreOffice and the `appy.pod <http://appyframework.org/pod.html>`__
package.

See also :ref:`lino.admin.appypod` and :doc:`/specs/appypod`.
"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    verbose_name = _("Appy POD")


    def get_used_libs(self, html=None):
        try:
            #~ import appy
            from appy import version
            version = version.verbose
        except ImportError:
            version = self.site.not_found_msg
        yield ("Appy", version, "http://appyframework.org/pod.html")

    
