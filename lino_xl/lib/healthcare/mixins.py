# Copyright 2018-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from lino.api import dd, _


class Tariffs(dd.ChoiceList):
    verbose_name = _("Healthcare tariff")
    verbose_name_plural = _("Healthcare tariffs")
add = Tariffs.add_item
add('10', _('Normal'), 'normal')
add('20', _('BIM'), 'bim')
add('30', _('OMNIO'), 'omnio')


class HealthcareSubject(dd.Model):

    class Meta:
        abstract = True

    # healthcare_provider = dd.ForeignKey(
    #     'contacts.Company',
    #     related_name="healthcare_subjects_by_provider",
    #     verbose_name=_("Healthcare provider"),
    #     blank=True, null=True)

    healthcare_tariff = Tariffs.field(default="normal", verbose_name=_("Tariff"))

    healthcare_plan = dd.ForeignKey(
        'healthcare.Plan', blank=True, null=True)
