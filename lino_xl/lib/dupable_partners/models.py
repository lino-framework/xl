# -*- coding: UTF-8 -*-
# Copyright 2014-2015 Luc Saffre
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
Database models for `lino_xl.lib.dupable_partners`.
"""

from lino.api import dd, _

from lino.mixins.dupable import PhoneticWordBase, SimilarObjects


class Word(PhoneticWordBase):
    """Phonetic words for Partners."""

    class Meta:
        verbose_name = _("Phonetic word")
        verbose_name_plural = _("Phonetic words")

    owner = dd.ForeignKey('contacts.Partner', related_name='dupable_words')


class Words(dd.Table):
    model = 'dupable_partners.Word'
    required_roles = dd.required(dd.SiteStaff)


class SimilarPartners(SimilarObjects):
    label = _("Similar partners")

