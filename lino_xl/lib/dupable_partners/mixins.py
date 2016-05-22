# -*- coding: UTF-8 -*-
# Copyright 2015 Luc Saffre
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

from lino.mixins.dupable import Dupable


class DupablePartner(Dupable):
    """Model mixin to add to the base classes of your application's
    `contacts.Partner` model.

    Note that using the mixin does not yet install the plugin, it just
    declares a model as being dupable. In order to activate
    verification, you must also add
    :mod:`lino_xl.lib.dupable_partners` to your
    :meth:`get_installed_apps
    <lino.core.site.Site.get_installed_apps>` method.

    """

    class Meta:
        abstract = True

    dupable_word_model = 'dupable_partners.Word'


class DupablePerson(DupablePartner):

    class Meta:
        abstract = True

    def dupable_matches_required(self):
        """Two persons named *Marie-Louise Dupont* and *Marie-Louise
        Vandenmeulenbos* should *not* match.

        """
        first = self.get_dupable_words(self.first_name)
        return max(2, len(first)+1)

    def unused_find_similar_instances(self, limit, **kwargs):
        first = self.get_dupable_words(self.first_name)
        if len(first) <= 1:
            super(DupablePerson, self).find_similar_instances(limit, **kwargs)
        lst = []
        i = 0

        def matches(other):
            return True

        for o in super(DupablePerson, self).find_similar_instances(
                None, **kwargs):
            if matches(self, o):
                lst.append(o)
                i += 1
                if i >= limit:
                    break
        return lst
            
