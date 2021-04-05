# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

from __future__ import unicode_literals

from django.conf import settings
from lino.api import dd, rt, _
from lino.utils import Cycler

# Questions originally copied from https://www.politicalcompass.org
QUESTIONS = """

= Just a few propositions to start with, concerning — no less — how you see the country and the world.

If economic globalisation is inevitable, it should primarily serve humanity rather than the interests of trans-national corporations.

I'd always support my country, whether it was right or wrong.

No one chooses his or her country of birth, so it's foolish to be proud of it.

Our race has many superior qualities, compared with other races.

The enemy of my enemy is my friend.

Military action that defies international law is sometimes justified.

There is now a worrying fusion of information and entertainment.

= Now, the economy. We're talking attitudes here, not the FTSE index.

People are ultimately divided more by class than by nationality.

Controlling inflation is more important than controlling unemployment.

Because corporations cannot be trusted to voluntarily protect the environment, they require regulation.

"from each according to his ability, to each according to his need" is a fundamentally good idea.

It's a sad reflection on our society that something as basic as drinking water is now a bottled, branded consumer product.

Land shouldn't be a commodity to be bought and sold.

It is regrettable that many personal fortunes are made by people who simply manipulate money and contribute nothing to their society.

Protectionism is sometimes necessary in trade.

The only social responsibility of a company should be to deliver a profit to its shareholders.

The rich are too highly taxed.

Those with the ability to pay should have access to higher standards of medical care.

Governments should penalise businesses that mislead the public.

A genuine free market requires restrictions on the ability of predator multinationals to create monopolies.

The freer the market, the freer the people.

"""

def objects():

    polls = rt.models.polls

    agree = polls.ChoiceSet.objects.get(
        **dd.str2kw('name', _("Agree-Disagree")))
        
    USERS = Cycler(settings.SITE.user_model.objects.all())

    def poll(choiceset, title, details, questions):
        return polls.Poll(
            user=USERS.pop(),
            title=title.strip(),
            details=details.strip(),
            state=polls.PollStates.active,
            questions_to_add=questions,
            default_choiceset=choiceset)

    yield poll(
        agree,
        "Political compass",
        "First two pages of [url https://www.politicalcompass.org/test]",
        QUESTIONS)
