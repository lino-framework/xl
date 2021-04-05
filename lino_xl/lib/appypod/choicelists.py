# -*- coding: UTF-8 -*-
# Copyright 2009-2020 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

import logging; logger = logging.getLogger(__name__)

import os

from django.conf import settings
from django.utils import translation

from lino.modlib.printing.choicelists import SimpleBuildMethod, BuildMethods

from .appy_renderer import AppyRenderer
try:
    from appy.pod.actions import EvaluationError
except ImportError:
    try:
        from appy.pod.buffers import EvaluationError
    except ImportError:
        EvaluationError = Exception
        # Run the python manage.py install to install appy correctly.


class AppyBuildMethod(SimpleBuildMethod):

    template_ext = '.odt'
    templates_name = 'appy'  # subclasses use the same templates directory
    default_template = 'Default.odt'

    def simple_build(self, ar, elem, tpl, target):
        # When the source string contains non-ascii characters, then
        # we must convert it to a unicode string.
        lang = str(elem.get_print_language()
                   or settings.SITE.DEFAULT_LANGUAGE.django_code)
        if False:  # debugging
            logger.info(
                u"appy.pod render %s -> %s (language=%r,params=%s",
                tpl, target, lang, settings.SITE.appy_params)
        else:
            logger.info("appy.pod render %s -> %s", tpl, target)

        with translation.override(lang):

            context = elem.get_printable_context(ar)
            # 20150721 context.update(ar=ar)

            # backwards compat for existing .odt templates.  Cannot
            # set this earlier because that would raise an exception
            # "render() got multiple values for keyword argument
            # 'self'".
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
    target_ext = '.odt'
    cache_name = 'userdocs'
    #~ cache_name = 'webdav'
    use_webdav = True


class AppyPdfBuildMethod(AppyBuildMethod):
    target_ext = '.pdf'


class AppyRtfBuildMethod(AppyBuildMethod):
    target_ext = '.rtf'
    cache_name = 'userdocs'
    use_webdav = True


class AppyDocBuildMethod(AppyBuildMethod):
    target_ext = '.doc'
    cache_name = 'userdocs'
    use_webdav = True


add = BuildMethods.add_item_instance
add(AppyOdtBuildMethod('appyodt'))
add(AppyDocBuildMethod('appydoc'))
add(AppyPdfBuildMethod('appypdf'))
add(AppyRtfBuildMethod('appyrtf'))
