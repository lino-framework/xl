# -*- coding: UTF-8 -*-
# Copyright 2008-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from lino.api import dd, rt, _

class DoYouLike(dd.ChoiceList):
    verbose_name = _("Do you like?")

add = DoYouLike.add_item
add('0', _("certainly not"))
add('1', _("rather not"))
add('2', _("normally"), "default")
add('3', _("quite much"))
add('4', _("very much"))


class HowWell(dd.ChoiceList):

    verbose_name = _("How well?")

add = HowWell.add_item
add('0', _("not at all"))
add('1', _("a bit"))
add('2', _("moderate"), "default")
add('3', _("quite well"))
add('4', _("very well"))
