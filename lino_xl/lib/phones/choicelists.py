# Copyright 2017 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)


from django.core.validators import validate_email, URLValidator

from etgen.html import E
from lino.api import dd, _
from lino.modlib.office.roles import OfficeStaff


validate_url = URLValidator()


class ContactDetailType(dd.Choice):
    field_name = None
    
    def format(self, value):
        return value

    def validate(self, value):
        return value

    def as_html(self, obj, ar):
        return obj.value

STD = ContactDetailType

class EMAIL(ContactDetailType):
    def validate(self, value):
        validate_email(value)

    def as_html(self, obj, ar):
        return E.a(obj.value, href="mailto:" + obj.value)


class URL(ContactDetailType):
    def validate(self, value):
        validate_url(value)

    def as_html(self, obj, ar):
        txt = obj.remark or obj.value
        return E.a(txt, href=obj.value)



class ContactDetailTypes(dd.ChoiceList):
    required_roles = dd.login_required(OfficeStaff)
    verbose_name = _("Contact detail type")
    verbose_name_plural = _("Contact detail types")
    item_class = ContactDetailType

add = ContactDetailTypes.add_item_instance
add(EMAIL('010', _("E-Mail"), 'email', field_name="email"))
add(STD('020', _("Mobile"), 'gsm', field_name="gsm"))
add(STD('030', _("Phone"), 'phone', field_name="phone"))
add(URL('040', _("Website"), 'url', field_name="url"))
add(STD('050', _("Fax"), 'fax', field_name="fax"))
add(STD('090', _("Other"), 'other'))


