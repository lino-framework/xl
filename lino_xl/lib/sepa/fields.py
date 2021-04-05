# Copyright 2014-2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Defines entry fields for IBAN and BIC.

"""

from django.db import models

from localflavor.generic import models as iban_fields
from localflavor.generic.forms import IBANFormField

from lino.api import dd

from lino.utils.jsgen import js_code
import six


from lino.core.elems import CharFieldElement
#from lino.modlib.extjs.ext_renderer import ExtRenderer

IBAN_FORMFIELD = IBANFormField()

class UppercaseTextFieldElement(CharFieldElement):
    """A CharFieldElement which accepts only upper-case characters.
    """
    value_template = "new Lino.UppercaseTextField(%s)"

class IBANFieldElement(UppercaseTextFieldElement):
    def get_column_options(self, **kw):
        """
        Return a string to be used as `Ext.grid.Column.renderer
        <http://docs.sencha.com/extjs/3.4.0/#!/api/Ext.grid.Column-cfg-renderer>`.
        """
        kw = super(
            UppercaseTextFieldElement, self).get_column_options(**kw)
        kw.update(renderer=js_code('Lino.iban_renderer'))
        return kw


class UppercaseTextField(models.CharField, dd.CustomField):
    """A custom CharField that accepts only uppercase caracters."""
    def create_layout_elem(self, rnd, cl, *args, **kw):
        # cl is the CharFieldElement class of the renderer
        return UppercaseTextFieldElement(*args, **kw)

    def to_python(self, value):
        if isinstance(value, six.string_types):
            return value.upper()
        return value

    def get_prep_value(self, value):
        return str(value) if value else ''


class BICField(iban_fields.BICField, UppercaseTextField):
    """Database field used to store a BIC. """

    def from_db_value(self, value, expression, connection, context=None):
        return value


class IBANField(iban_fields.IBANField, dd.CustomField):
    """Database field used to store an IBAN. """

    def from_db_value(self, value, expression, connection, context=None):
        return value

    def create_layout_elem(self, rnd, cl, *args, **kw):
        return IBANFieldElement(*args, **kw)
        # if isinstance(rnd, ExtRenderer):
        #     # cl is the CharFieldElement class of the renderer
        #     return IBANFieldElement(*args, **kw)
        # if isinstance(rnd, bootstrap3.Renderer):


    def to_python(self, value):
        if isinstance(value, six.string_types):
            return value.upper().replace(' ', '')
        return value

    # def get_column_renderer(self):
    #     return 'Lino.iban_renderer'
