# -*- coding: UTF-8 -*-
# Copyright 2012-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.

"""
This fixture defines the content for pages `/man` and below.
Another attempt to provide a user manual.

This is a "reloadable" fixture. If you say::

  python manage.py loaddata man
  
it will overwrite existing web pages.

"""

from __future__ import unicode_literals

from django.conf import settings

from lino_xl.lib.pages.builder import page, objects

page('man', 'en', 'User manual', """
This is the user manual for 
`{{site.verbose_name}} <{{site.url}}>`__
version {{site.version}}.
""")

page('man', 'de', 'Benutzerhandbuch', """
Benutzerhandbuch für 
`{{site.verbose_name}} <{{site.url}}>`__
version {{site.version}}.
""")

page('models', 'en', 'Model reference', """
These are the models used in {{site.verbose_name}}.

{{as_table('about.Models')}}

""", parent='man')
