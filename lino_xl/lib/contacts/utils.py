# -*- coding: UTF-8 -*-
# Copyright 2010-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Some utilities for parsing contact data. See also
:mod:`lino.mixins.human`.

- :func:`street2kw` to separate house number and optional
  flat number from street

"""

import re


def street2kw(s, **kw):
    """
Parse a string to extract the fields street, street_no and street_box.

Examples:

>>> from pprint import pprint
>>> pprint(street2kw("Limburger Weg"))
{'street': 'Limburger Weg'}
>>> pprint(street2kw("Loten 3"))
{'street': 'Loten', 'street_box': '', 'street_no': '3'}
>>> pprint(street2kw("Loten 3A"))
{'street': 'Loten', 'street_box': 'A', 'street_no': '3'}

>>> pprint(street2kw("In den Loten 3A"))
{'street': 'In den Loten', 'street_box': 'A', 'street_no': '3'}

>>> pprint(street2kw("Auf'm Bach"))
{'street': "Auf'm Bach"}
>>> pprint(street2kw("Auf'm Bach 3"))
{'street': "Auf'm Bach", 'street_box': '', 'street_no': '3'}
>>> pprint(street2kw("Auf'm Bach 3a"))
{'street': "Auf'm Bach", 'street_box': 'a', 'street_no': '3'}
>>> pprint(street2kw("Auf'm Bach 3 A"))
{'street': "Auf'm Bach", 'street_box': 'A', 'street_no': '3'}

Some rather special cases:

>>> pprint(street2kw("rue des 600 Franchimontois 1"))
{'street': 'rue des 600 Franchimontois', 'street_box': '', 'street_no': '1'}

>>> pprint(street2kw("Eupener Strasse 321 /A"))
{'street': 'Eupener Strasse', 'street_box': '/A', 'street_no': '321'}

>>> pprint(street2kw("Neustr. 1 (Referenzadr.)"))
{'addr2': '(Referenzadr.)', 'street': 'Neustr.', 'street_no': '1'}

Edge cases:

>>> street2kw("")
{}

    """
    #~ m = re.match(r"(\D+),?\s*(\d+)\s*(\w*)", s)
    m = re.match(r"(.+),?\s+(\d+)\s*(\D*)$", s)
    if m:
        kw['street'] = m.group(1).strip()
        kw['street_no'] = m.group(2).strip()
        street_box = m.group(3).strip()
        if len(street_box) > 5:
            kw['addr2'] = street_box
        else:
            kw['street_box'] = street_box
    else:
        s = s.strip()
        if len(s):
            kw['street'] = s
    return kw


def _test():
    import doctest
    doctest.testmod()

if __name__ == "__main__":
    _test()
