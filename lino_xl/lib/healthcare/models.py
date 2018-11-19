# Copyright 2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from lino.utils.mldbc.mixins import BabelDesignated
from lino.mixins.ref import Referrable

from lino.api import dd, _
from lino_xl.lib.contacts.roles import ContactsStaff

class Plan(Referrable, BabelDesignated):
    ref_max_length = 10
    class Meta:
        app_label = 'healthcare'
        abstract = dd.is_abstract_model(__name__, 'Plan')
        verbose_name = _("Healthcare plan")
        verbose_name_plural = _("Healthcare plans")

    provider = dd.ForeignKey(
        'contacts.Company',
        related_name="healthcare_plans_by_provider",
        verbose_name=_("Healthcare provider"),
        blank=True, null=True)

class Rule(dd.Model):

    class Meta:
        app_label = 'healthcare'
        abstract = dd.is_abstract_model(__name__, 'Rule')
        verbose_name = _("Healthcare rule")
        verbose_name_plural = _("Healthcare rules")

    plan = dd.ForeignKey('healthcare.Plan')
    
    client_fee = dd.ForeignKey(
        'products.Product',
        related_name="healthcare_plans_by_client_fee",
        verbose_name=_("Client fee"),
        blank=True, null=True)

    provider_fee = dd.ForeignKey(
        'products.Product',
        verbose_name=_("Provider fee"),
        related_name="healthcare_plans_by_provider_fee",
        blank=True, null=True)
    

class Plans(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = "healthcare.Plan"
    column_names = "ref designation provider *"
    detail_layout = """
    ref provider
    designation 
    RulesByPlan
    """
    insert_layout = """
    ref provider
    designation 
    """
class Rules(dd.Table):
    required_roles = dd.login_required(ContactsStaff)
    model = "healthcare.Rule"
    
class RulesByPlan(Rules):
    column_names = "client_fee provider_fee *"
    
