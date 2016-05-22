# -*- coding: UTF-8 -*-
# Copyright 2009-2016 Luc Saffre
#
# This file is part of Lino XL.
#
# Lino XL is free software: you can redistribute it and/or modify it
# under the terms of the GNU Affero General Public License as
# published by the Free Software Foundation, either version 3 of the
# License, or (at your option) any later version.
#
# Lino XL is distributed in the hope that it will be useful, but
# WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
# Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License along with Lino XL.  If not, see
# <http://www.gnu.org/licenses/>.
"""Choicelists for `lino_xl.lib.appypod`.
"""

from __future__ import unicode_literals

import logging
logger = logging.getLogger(__name__)

import os

from django.conf import settings
from django.utils import translation

from lino.modlib.printing.choicelists import SimpleBuildMethod, BuildMethods

from .appy_renderer import AppyRenderer
try:
    from appy.pod.actions import EvaluationError
except ImportError:
    from appy.pod.buffers import EvaluationError


class AppyBuildMethod(SimpleBuildMethod):
    """
    Base class for Build Methods that use `.odt` templates designed
    for :term:`appy.pod`.
    
    http://appyframework.org/podRenderingTemplates.html
    """

    template_ext = '.odt'
    templates_name = 'appy'  # subclasses use the same templates directory
    default_template = 'Default.odt'

    def simple_build(self, ar, elem, tpl, target):
        # When the source string contains non-ascii characters, then
        # we must convert it to a unicode string.
        lang = str(elem.get_print_language()
                   or settings.SITE.DEFAULT_LANGUAGE.django_code)
        logger.info(u"appy.pod render %s -> %s (language=%r,params=%s",
                    tpl, target, lang, settings.SITE.appy_params)

        with translation.override(lang):

            context = elem.get_printable_context(ar)
            # 20150721 context.update(ar=ar)

            # backwards compat for existing .odt templates.  Cannot
            # set this earlier because that would cause "render() got
            # multiple values for keyword argument 'self'" exception
            context.update(self=context['this'])
            try:
                AppyRenderer(ar, tpl, context, target,
                             **settings.SITE.appy_params).run()
            except EvaluationError as e:
                if True:
                    raise
                else:
                    raise Exception(
                        "Exception while rendering {0} ({1}) : {2}".format(
                            tpl, context, e))
        return os.path.getmtime(target)


class AppyOdtBuildMethod(AppyBuildMethod):
    """
    Generates .odt files from .odt templates.
    
    This method doesn't require OpenOffice nor the
    Python UNO bridge installed
    (except in some cases like updating fields).
    """
    target_ext = '.odt'
    cache_name = 'userdocs'
    #~ cache_name = 'webdav'
    use_webdav = True


class AppyPdfBuildMethod(AppyBuildMethod):
    """
    Generates .pdf files from .odt templates.
    """
    target_ext = '.pdf'


class AppyRtfBuildMethod(AppyBuildMethod):
    """
    Generates .rtf files from .odt templates.
    """
    target_ext = '.rtf'
    cache_name = 'userdocs'
    use_webdav = True


class AppyDocBuildMethod(AppyBuildMethod):
    """
    Generates .doc files from .odt templates.
    """
    target_ext = '.doc'
    cache_name = 'userdocs'
    use_webdav = True


add = BuildMethods.add_item_instance
add(AppyOdtBuildMethod('appyodt'))
add(AppyDocBuildMethod('appydoc'))
add(AppyPdfBuildMethod('appypdf'))
add(AppyRtfBuildMethod('appyrtf'))
