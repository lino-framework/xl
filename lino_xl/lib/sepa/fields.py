# Copyright 2014-2015 Luc Saffre
# This file is part of Lino Cosi.
#
# Lino Cosi is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino Cosi is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino Cosi.  If not, see
# <http://www.gnu.org/licenses/>.

"""Defines entry fields for IBAN and BIC.

"""

from django.db import models

from localflavor.generic import models as iban_fields
from localflavor.generic.forms import IBANFormField

from django.utils.six import with_metaclass

from lino.api import dd

from lino.utils.jsgen import js_code
from lino.modlib.extjs.elems import CharFieldElement
import six
# from lino_extjs6.extjs6.elems import CharFieldElement
# TODO: support ExtJS6

IBAN_FORMFIELD = IBANFormField()


class UppercaseTextFieldElement(CharFieldElement):
    """A CharFieldElement which accepts only upper-case characters.
    """
    value_template = "new Lino.UppercaseTextField(%s)"


class IBANFieldElement(UppercaseTextFieldElement):
    def get_column_options(self, **kw):
        """Return a string to be used as `Ext.grid.Column.renderer
        <http://docs.sencha.com/extjs/3.4.0/#!/api/Ext.grid.Column-cfg-renderer>`.

        """
        kw = super(
            UppercaseTextFieldElement, self).get_column_options(**kw)
        kw.update(renderer=js_code('Lino.iban_renderer'))
        return kw


class UppercaseTextField(models.CharField, dd.CustomField):
    """A custom CharField that accepts only uppercase caracters."""
    def create_layout_elem(self, *args, **kw):
        return UppercaseTextFieldElement(*args, **kw)

    def to_python(self, value):
        if isinstance(value, six.string_types):
            return value.upper()
        return value

    def get_prep_value(self, value):
        return str(value) if value else ''


class BICField(iban_fields.BICField, UppercaseTextField):
    """Database field used to store a BIC. """

    def from_db_value(self, value, expression, connection, context):
        return value


class IBANField(iban_fields.IBANField, dd.CustomField):
    """Database field used to store an IBAN. """

    def from_db_value(self, value, expression, connection, context):
        return value

    def create_layout_elem(self, *args, **kw):
        return IBANFieldElement(*args, **kw)

    def to_python(self, value):
        if isinstance(value, six.string_types):
            return value.upper().replace(' ', '')
        return value

    # def get_column_renderer(self):
    #     return 'Lino.iban_renderer'


