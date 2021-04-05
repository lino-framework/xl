# Copyright 2017 Tonis Piip, Rumma & Ko Ltd
#
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""Adds a radicale caldav server to the application.

Requires radicale to be installed.


.. autosummary::
    :toctree:

    views

"""

import logging

from lino import ad
from django.utils.translation import gettext_lazy as _
from . import views

from django.conf.urls import url
# import radicale.config
# import radicale.log

# try:
#     from configparser import RawConfigParser as ConfigParser
# except ImportError:
#     from ConfigParser import RawConfigParser as ConfigParser

# try:
#     from io import StringIO as StringIO
# except ImportError:
#     from StringIO import StringIO as StringIO

# Django autoreload fails when some value in settings is not
# hashable. So we use a hack copied from
# https://github.com/kyokenn/djradicale/blob/master/djradicale/__init__.py

# class HashableConfigParser(ConfigParser):
#     def __hash__(self):
#         output = StringIO()
#         self.write(output)
#         hash_ = hash(output.getvalue())
#         output.close()
#         return hash_

# radicale.config.__class__ = HashableConfigParser

# radicale.log.LOGGER = logging.Logger("maildev")
# # fh = logging.FileHandler('/home/luc/rad.log')
# # fh.setLevel(logging.DEBUG)
# ch = logging.StreamHandler()
# # ch.setLevel(logging.DEBUG)
# # radicale.log.LOGGER.addHandler(fh)
# radicale.log.LOGGER.addHandler(ch)

class Plugin(ad.Plugin):

    verbose_name = _("CalDav")
    needs_plugins = ['lino.xl.cal']

    # RADICALE_CONFIG = {
    # 'server': {
    #     'base_prefix': '/.rad/',
    #     'realm': 'Radicale - Password Required',
    # },
    # 'logging':{
    #     'debug':True

    # },
    # 'encoding': {
    #     'request': 'utf-8',
    #     'stock': 'utf-8',
    # },
    # 'auth': {
    #     'type': 'custom',
    #     'custom_handler': 'djradicale.auth.django',
    # },
    # 'rights': {
    #     'type': 'custom',
    #     'custom_handler': 'djradicale.rights.django',
    # },
    # 'storage': {
        # 'type': 'filesystem',
        # 'type': 'custom',
        # 'filesystem_folder' : '~/.config/foo/radicale/collections',
     # },
    #     'custom_handler': 'djradicale.storage.django',
    # },
    # 'well-known': {
    #     'carddav': '/pim/%(user)s/addressbook.vcf',
    #     'caldav': '/pim/%(user)s/calendar.ics',
    # },
    # }

    # radicale.log.LOGGER.debug("xxxxxxxxxxxxxxx")

    # def on_init(self):
    #     for section, values in self.RADICALE_CONFIG.items():
    #         for key, value in values.items():
    #             if not radicale.config.has_section(section):
    #                 radicale.config.add_section(section)
    #             radicale.config.set(section, key, value)

    def get_patterns(self):
        return [
            url(r'^caldav/(?P<url>.*)$', views.CalDavView.as_view())
        ]

    def unused_get_middleware_classes(self):
        yield 'django.middleware.csrf.CsrfViewMiddleware'
        yield 'django.middleware.clickjacking.XFrameOptionsMiddleware'

    # for section, values in self.RADICALE_CONFIG.items():
    #     for key, value in values.items():
    #         if not radicale.config.has_section(section):
    #             radicale.config.add_section(section)
    #         radicale.config.set(section, key, value)
