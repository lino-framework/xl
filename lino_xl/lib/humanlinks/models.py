# -*- coding: UTF-8 -*-
# Copyright 2014-2018 Rumma & Ko Ltd
#
# License: BSD (see file COPYING for details)
"""
Database models for `lino_xl.lib.humanlinks`.

"""


from __future__ import unicode_literals
from __future__ import print_function
from builtins import str

import logging
logger = logging.getLogger(__name__)

from django.core.exceptions import ValidationError
#from django.utils.translation import ugettext_lazy as _
from django.db.models import Q
from lino_xl.lib.contacts.roles import ContactsUser, ContactsStaff

from lino.api import dd, rt, _, gettext
from etgen.html import E
from .choicelists import LinkTypes

config = dd.plugins.humanlinks



class Link(dd.Model):
    """A link between two persons.

    .. attribute:: parent

        Pointer to the person who is "parent".

    .. attribute:: child

        Pointer to the person who is "child".

    .. attribute:: type

        The type of link.  Pointer to :class:`LinkTypes
        <lino_xl.lib.humanlinks.choicelists.LinkTypes>`.

    """
    class Meta:
        verbose_name = _("Personal Link")
        verbose_name_plural = _("Personal Links")

    type = LinkTypes.field(default=LinkTypes.as_callable('parent'))
    parent = dd.ForeignKey(
        config.person_model,
        verbose_name=_("Who is..."),
        related_name='humanlinks_children')
    child = dd.ForeignKey(
        config.person_model,
        blank=True, null=True,
        verbose_name=_("To whom..."),
        related_name='humanlinks_parents')

    @dd.displayfield(_("Type"))
    def type_as_parent(self, ar):
        # print('20140204 type_as_parent', self.type)
        return self.type.as_parent(self.parent)

    @dd.displayfield(_("Type"))
    def type_as_child(self, ar):
        # print('20140204 type_as_child', self.type)
        return self.type.as_child(self.child)

    def __str__(self):
        if self.type is None:
            return super(Link, self).__str__()
        return _("%(child)s is %(what)s") % dict(
            child=str(self.child),
            what=self.type_of_parent_text())

    def type_of_parent_text(self):
        return _("%(type)s of %(parent)s") % dict(
            parent=self.parent,
            type=self.type.as_child(self.child))

    parent_link_types = (LinkTypes.parent, LinkTypes.adoptive_parent,
                         LinkTypes.foster_parent)

    @classmethod
    def check_autocreate(cls, parent, child):
        """Check whether there is a human link of type "parent" between the
        given persons. Create one if not. If the child has already
        another parent of same sex, then it becomes a foster child,
        otherwise a natural child.

        Note that the ages are ignored here, Lino will shamelessly
        create a link even when the child is older than the parent.

        This is called from :meth:`full_clean` of
        :class:`lino_xl.lib.households.Member` to
        automatically create human links between two household
        members.

        """
        if parent is None or child is None:
            return False
        if parent == child:
            return False
            # raise ValidationError("Parent and Child must differ")
        qs = cls.objects.filter(
            parent=parent, child=child, type__in=cls.parent_link_types)
        if qs.count() == 0:
            qs = cls.objects.filter(
                child=child, type__in=cls.parent_link_types,
                parent__gender=parent.gender)
            if qs.count() == 0:
                auto_type = LinkTypes.parent
            else:
                auto_type = LinkTypes.foster_parent
            obj = cls(parent=parent, child=child, type=auto_type)
            obj.full_clean()
            obj.save()
            # dd.logger.info("20141018 autocreated %s", obj)
            return True
        return False


class Links(dd.Table):
    model = 'humanlinks.Link'
    required_roles = dd.login_required(ContactsStaff)
    stay_in_grid = True
    detail_layout = dd.DetailLayout("""
    parent
    type
    child
    """, window_size=(40, 'auto'))
    
    insert_layout = """
    parent
    type
    child
    """



class LinksByHuman(Links):
    """Show all links for which this human is either parent or child.

    Display all human links of the master, using both the parent and
    the child directions.

    It is a cool usage example for using a :meth:`get_request_queryset
    <lino.core.actors.dbtable.Table.get_request_queryset>` method
    instead of :attr:`master_key
    <lino.core.actors.dbtable.Table.master_key>`.

    It is also a cool usage example for the
    :meth:`lino.core.actors.dbtable.Table.get_table_summary` method.

    """
    label = _("Human Links")
    required_roles = dd.login_required(ContactsUser)
    master = config.person_model
    column_names = 'parent type_as_parent:10 child'
    display_mode = 'summary'

    addable_link_types = (
        LinkTypes.parent, LinkTypes.adoptive_parent,
        LinkTypes.foster_parent,
        LinkTypes.spouse,
        LinkTypes.partner,
        LinkTypes.stepparent,
        LinkTypes.sibling,
        LinkTypes.cousin,
        LinkTypes.uncle,
        LinkTypes.relative, LinkTypes.other)

    @classmethod
    def get_request_queryset(self, ar, **filter):
        mi = ar.master_instance  # a Person
        Link = rt.models.humanlinks.Link
        if mi is None:
            return Link.objects.none()
        flt = Q(parent=mi) | Q(child=mi)
        return Link.objects.filter(flt).order_by(
            'child__birth_date', 'parent__birth_date')

    @classmethod
    def get_table_summary(self, obj, ar):
        """The :meth:`summary view <lino.core.actors.Actor.get_table_summary>`
        for :class:`LinksByHuman`.

        """
        if obj is None:
            return ''
        # if obj.pk is None:
        #     return ''
        #     raise Exception("20150218")
        sar = self.request_from(ar, master_instance=obj)
        links = []
        for lnk in sar:
            if lnk.parent is None or lnk.child is None:
                pass
            else:
                if lnk.child_id == obj.id:
                    i = (lnk.type.as_child(obj), lnk.parent)
                else:
                    i = (lnk.type.as_parent(obj), lnk.child)
                links.append(i)

        try:
            links.sort(
                key=lambda a: a[1].birth_date.as_date(), reverse=True)
        # except AttributeError:
        except (AttributeError, ValueError):
            # AttributeError: 'str' object has no attribute 'as_date'
            # possible when empty birth_date
            # ValueError: day is out of range for month
            pass

        items = []
        for type, other in links:
            items.append(E.li(
                str(type), gettext(" of "),
                obj.format_family_member(ar, other),
                " (%s)" % other.age
            ))
        elems = []
        if len(items) > 0:
            elems += [gettext("%s is") % obj.first_name]
            elems.append(E.ul(*items))
        else:
            elems.append(gettext("No relationships."))

        # Buttons for creating relationships:
        if self.insert_action is not None:
            sar = self.insert_action.request_from(ar)
            if sar.get_permission():
                actions = []
                for lt in self.addable_link_types:
                    sar.known_values.update(type=lt, parent=obj)
                    sar.known_values.pop('child', None)
                    #sar = ar.spawn(self, known_values=dict(type=lt, parent=obj))
                    btn = sar.ar2button(None, lt.as_parent(obj), icon_name=None)
                    actions.append(btn)
                    if not lt.symmetric:
                        actions.append('/')
                        sar.known_values.update(type=lt, child=obj)
                        sar.known_values.pop('parent', None)
                        btn = sar.ar2button(None, lt.as_child(obj), icon_name=None)
                        actions.append(btn)
                    actions.append(' ')

                if len(actions) > 0:
                    elems += [E.br(), gettext("Create relationship as ")] + actions
        return E.div(*elems)


# __all__ = [
#     'LinkTypes',
#     'Link',
#     'Links',
#     'LinksByHuman'
#     ]

