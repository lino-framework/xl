# Copyright 2010-2019 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)


# This module is here e.g. for `lino.projects.docs` which installs the
# app but no BeIdCardHolder model.

from .choicelists import BeIdCardTypes, ResidenceTypes
from .mixins import BeIdCardHolder
