# -*- coding: UTF-8 -*-
# Copyright 2014-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from django.utils.translation import ugettext_lazy as _
from django.contrib.humanize.templatetags.humanize import naturaltime
from django.db import models

from lino.utils.mldbc.mixins import BabelNamed
from lino.modlib.printing.mixins import Printable

from lino.api import dd


class ClearPrinted(dd.Action):
    sort_index = 51
    label = _('Clear print cache')
    icon_name = 'printer_delete'

    # def get_action_permission(self, ar, obj, state):
    #     if obj is not None and obj.printed_by_id is None:
    #         return False
    #     return super(ClearPrinted, self).get_action_permission(
    #         ar, obj, state)

    def run_from_ui(self, ar, **kw):
        obj = ar.selected_rows[0]
        if obj.printed_by_id is None:
            ar.error(_("Oops, the print cache was already cleared."))
            return

        def ok(ar2):
            obj.clear_cache()
            ar2.success(_("Print cache file has been cleared."), refresh=True)
        if False:
            ar.confirm(
                ok,
                _("Going to clear the print cache file of %s") %
                dd.obj2unicode(obj))
        else:
            ok(ar)


class Certifiable(Printable):
    class Meta:
        abstract = True

    if dd.is_installed('excerpts'):

        printed_by = dd.ForeignKey(
            'excerpts.Excerpt',
            verbose_name=_("Printed"),
            editable=False,
            related_name="%(app_label)s_%(class)s_set_as_printed",
            blank=True, null=True, on_delete=models.SET_NULL)

        clear_printed = ClearPrinted()

        def disabled_fields(self, ar):
            # if self._state.adding:
            #     return set()
            s = super(Certifiable, self).disabled_fields(ar)
            # print("20191202 disabled_fields a", self, self.printed_by_id, s)
            if self.printed_by_id is None:
                s.add('clear_printed')
            else:
                s |= self.CERTIFIED_FIELDS
            # print("20191202 disabled_fields b", self, self.printed_by_id, s)
            return s

        def on_duplicate(self, ar, master):
            super(Certifiable, self).on_duplicate(ar, master)
            self.printed_by = None

        @classmethod
        def on_analyze(cls, site):
            # Contract.user.verbose_name = _("responsible (DSBE)")
            cls.CERTIFIED_FIELDS = dd.fields_list(
                cls,
                cls.get_certifiable_fields())
            super(Certifiable, cls).on_analyze(site)

        @classmethod
        def get_certifiable_fields(cls):
            """
            """
            return ''

        @dd.displayfield(_("Printed"))
        def printed(self, ar):
            if ar is None:
                return ''
            ex = self.printed_by
            if ex is None:
                return ''
            return ar.obj2html(ex, naturaltime(ex.build_time))

        def clear_cache(self):
            obj = self.printed_by
            if obj is not None:
                self.printed_by = None
                self.full_clean()
                self.save()
                obj.delete()

        def get_excerpt_title(self):
            return str(self)

        def get_excerpt_templates(self, bm):
            return None


class ExcerptTitle(BabelNamed):
    class Meta:
        abstract = True

    excerpt_title = dd.BabelCharField(
        _("Excerpt title"),
        max_length=200,
        blank=True,
        help_text=_(
            "The title to be used when printing an excerpt."))

    def get_excerpt_title(self):
        return dd.babelattr(self, 'excerpt_title') or str(self)
