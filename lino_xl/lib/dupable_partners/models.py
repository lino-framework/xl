# -*- coding: UTF-8 -*-
# Copyright 2014-2015 Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

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
    required_roles = dd.login_required(dd.SiteStaff)


class SimilarPartners(SimilarObjects):
    label = _("Similar partners")

