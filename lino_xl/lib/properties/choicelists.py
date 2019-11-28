# -*- coding: UTF-8 -*-
# Copyright 2008-2018 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


from lino.api import dd, rt, _

class DoYouLike(dd.ChoiceList):
    """A list of possible answers to questions of type "How much do you
    like ...?".

    """
    verbose_name = _("Do you like?")

add = DoYouLike.add_item
add('0', _("certainly not"))
add('1', _("rather not"))
add('2', _("normally"), "default")
add('3', _("quite much"))
add('4', _("very much"))


class HowWell(dd.ChoiceList):

    """A list of possible answers to questions of type "How well ...?":
    "not at all", "a bit", "moderate", "quite well" and "very well"

    which are stored in the database as '0' to '4',
    and whose `__str__()` returns their translated text.

    """
    verbose_name = _("How well?")

add = HowWell.add_item
add('0', _("not at all"))
add('1', _("a bit"))
add('2', _("moderate"), "default")
add('3', _("quite well"))
add('4', _("very well"))
