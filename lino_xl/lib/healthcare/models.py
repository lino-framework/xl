# Copyright 2018-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.api import dd, _
# from lino.utils.mldbc.mixins import BabelDesignated
from lino.mixins.ref import Referrable
from lino.mixins.periods import DateRange
from lino.mixins import Sequenced
from lino_xl.lib.contacts.roles import ContactsStaff, ContactsUser

from .mixins import HealthcareSubject, Tariffs


@dd.python_2_unicode_compatible
class Plan(Referrable):

    ref_max_length = 30

    class Meta:
        app_label = 'healthcare'
        abstract = dd.is_abstract_model(__name__, 'Plan')
        verbose_name = _("Healthcare plan")
        verbose_name_plural = _("Healthcare plans")

    provider = dd.ForeignKey(
        'contacts.Company',
        related_name="healthcare_plans_by_provider",
        verbose_name=_("Provider"),
        blank=True, null=True)

    remark = dd.CharField(_("Remark"), max_length=200, blank=True)

    def __str__(self):
        if self.ref:
            return self.ref
        else:
            return str(self.provider)


class Situation(DateRange, HealthcareSubject):

    class Meta:
        app_label = 'healthcare'
        abstract = dd.is_abstract_model(__name__, 'Situation')
        verbose_name = _("Healthcare situation")
        verbose_name_plural = _("Healthcare situations")

    # plan = dd.ForeignKey('healthcare.Plan', blank=True, null=True)
    client = dd.ForeignKey(dd.plugins.healthcare.client_model)


class Rule(Sequenced):

    class Meta:
        app_label = 'healthcare'
        abstract = dd.is_abstract_model(__name__, 'Rule')
        verbose_name = _("Healthcare rule")
        verbose_name_plural = _("Healthcare rules")

    plan = dd.ForeignKey('healthcare.Plan', blank=True, null=True)

    # provider = dd.ForeignKey(
    #     'contacts.Company',
    #     related_name="healthcare_rules_by_provider",
    #     verbose_name=_("Healthcare provider"),
    #     blank=True, null=True)

    tariff = Tariffs.field(blank=True, verbose_name=_("Tariff"))

    client_fee = dd.ForeignKey(
        'products.Product',
        related_name="healthcare_rules_by_client_fee",
        verbose_name=_("Client fee"),
        blank=True, null=True)

    provider_fee = dd.ForeignKey(
        'products.Product',
        verbose_name=_("Provider fee"),
        related_name="healthcare_rules_by_provider_fee",
        blank=True, null=True)
    

class Plans(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = "healthcare.Plan"
    column_names = "ref provider remark *"
    detail_layout = """
    ref provider
    remark
    RulesByPlan
    """
    insert_layout = """
    ref provider
    remark
    """


class Situations(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = "healthcare.Situation"


class SituationsByClient(Situations):
    required_roles = dd.login_required(ContactsUser)
    master_key = "client"
    column_names = "start_date end_date healthcare_plan healthcare_tariff *"


class Rules(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = "healthcare.Rule"
    column_names = "plan tariff client_fee provider_fee *"

class RulesByPlan(Rules):
    master_key = "plan"
    column_names = "tariff client_fee provider_fee *"

