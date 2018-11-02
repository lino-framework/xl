# -*- coding: UTF-8 -*-
# Copyright 2011-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

import os
from builtins import str

from django.conf import settings
from lino.utils import format_date
from lino.utils.media import TmpMediaFile
from lino.core import actions
from lino.api import dd, rt, _

from .appy_renderer import AppyRenderer


class PrintTableAction(actions.Action):
    label = _("Table (landscape)")
    icon_name = 'page_white_acrobat'
    ui5_icon_name = 'sap-icon://pdf-attachment'

    sort_index = -10
    select_rows = False
    default_format = 'ajax'
    show_in_bbar = True
    preprocessor = "Lino.get_current_grid_config"
    # MAX_ROW_COUNT = 900
    template_name = "Table.odt"
    target_file_format = 'pdf'  # can be pdf, odt or rtf
    # target_file_format = 'odt'  # write to odt to see error messages
                                  # for debugging templates
    combo_group = 'pdf'
    callable_from = 't'

    # def is_callable_from(self, caller):
    #     return isinstance(caller, actions.ShowTable)

    def run_from_ui(self, ar, **kw):
        #~ print 20130912
        #~ obj = ar.selected_rows[0]
        mf = TmpMediaFile(ar, self.target_file_format)
        settings.SITE.makedirs_if_missing(os.path.dirname(mf.name))
        self.appy_render(ar, mf.name)
        ar.set_response(success=True)
        ar.set_response(open_url=mf.get_url(ar.request))
        #~ return http.HttpResponseRedirect(mf.url)
        #~ return kw

    def appy_render(self, ar, target_file):

        # if ar.get_total_count() > self.MAX_ROW_COUNT:
        #     raise Exception(_("List contains more than %d rows") %
        #                     self.MAX_ROW_COUNT)

        tplfile = rt.find_config_file(self.template_name, '')
        if not tplfile:
            raise Exception("No file %s" % self.template_name)

        # 20150810 ar.renderer = settings.SITE.kernel.html_renderer  # 20120624

        context = self.get_context(ar)
        if os.path.exists(target_file):
            os.remove(target_file)
        dd.logger.debug(u"appy.pod render %s -> %s (params=%s",
                        tplfile, target_file, settings.SITE.appy_params)
        renderer = AppyRenderer(
            ar, tplfile, context, target_file, **settings.SITE.appy_params)
        renderer.run()

    def get_context(self, ar):
        return dict(
            ar=ar,
            title=str(ar.get_title()),
            dtos=format_date.dtos,
            dtosl=format_date.dtosl,
            dtomy=format_date.fdmy,
            babelattr=settings.SITE.babelattr,
            babelitem=settings.SITE.babelitem,
            tr=settings.SITE.babelitem,
            settings=settings,
            _=_,
            #~ knowledge_text=fields.knowledge_text,
        )


class PortraitPrintTableAction(PrintTableAction):
    label = _("Table (portrait)")
    template_name = "Table-portrait.odt"
    sort_index = -9


class PrintLabelsAction(PrintTableAction):

    label = _("Labels")
    help_text = _('Generate mailing labels for these recipients')
    template_name = "appypod/Labels.odt"
    sort_index = -8

    def get_context(self, ar):
        context = super(PrintLabelsAction, self).get_context(ar)
        context.update(recipients=self.get_recipients(ar))
        return context

    def get_recipients(self, ar):
        return iter(ar)
