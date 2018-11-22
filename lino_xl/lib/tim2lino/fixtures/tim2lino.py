# -*- coding: UTF-8 -*-
# Copyright 2009-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from importlib import import_module
from django.conf import settings

def objects():
    mod = import_module(settings.SITE.plugins.tim2lino.timloader_module)
    tim = mod.TimLoader(settings.SITE.legacy_data_path)
    for obj in tim.objects():
        yield obj

    tim.finalize()
