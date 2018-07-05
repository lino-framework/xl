# -*- coding: UTF-8 -*-
# Copyright 2013-2018 Rumma & Ko Ltd

"""
An extension to :mod:`lino_xl.lib.cal` which uses the `Extensible
<http://ext.ensible.com>`_ calendar library to add a special "Calendar
Panel" view of your calendar events.

This plugin is deprecated since Lino is migrating away from ExtJS.
See also Brians blog post `End of the Line
<http://ext.ensible.com/blog/2016/06/end-of-the-line/>`__.

Using this plugin in your application requires you to either publish
your application under a license compatible with the GNU GPL license
v3, or to purchase a commercial licence from Extensible.  See
`Extensible Licensing Overview
<http://ext.ensible.com/products/licensing/>`__.
"""

from lino.api import ad


class Plugin(ad.Plugin):
    "Extends :class:`lino.core.plugin.Plugin`."

    verbose_name = "Ext.ensible adapter"

    calendar_start_hour = 8  # setting
    """
    The time at which the CalendarPanel's daily view starts.
    """

    calendar_end_hour = 18  # setting
    """
    The time at which the CalendarPanel's daily view ends.
    """

    site_js_snippets = ['snippets/extensible.js']
    media_name = 'extensible-1.0.1'
    # media_base_url = "http://ext.ensible.com/deploy/1.0.2/"

    def get_used_libs(self, html=None):
        if html:
            onclick = "alert('Extensible Calendar version is ' \
            + Ext.ensible.version);"
            tip = "Click to see Extensible Calendar version"
            text = "(version)"
            version = html.a(text, href='#', onclick=onclick, title=tip)
            yield (self.verbose_name, version,
                   "http://ext.ensible.com/products/calendar/")

    def get_css_includes(self, site):
        yield self.build_lib_url('resources/css/extensible-all.css')

    def get_js_includes(self, settings, language):
        if settings.DEBUG:
            yield self.build_lib_url('extensible-all-debug.js')
        else:
            yield self.build_lib_url('extensible-all.js')
        if language != 'en':
            yield self.build_lib_url(
                'src', 'locale',
                'extensible-lang-' + language + '.js')

    def setup_main_menu(config, site, user_type, m):
        m = m.add_menu("cal", site.plugins.cal.verbose_name)
        # m = m.add_menu("cal", _("Calendar"))
        m.add_action('extensible.CalendarPanel')


