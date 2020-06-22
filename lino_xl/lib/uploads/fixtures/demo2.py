# -*- coding: UTF-8 -*-
# Copyright 2015-2020 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

from builtins import range
from django.conf import settings
from lino.utils import Cycler
from lino.api import dd, rt

def objects():
    Upload = rt.models.uploads.Upload
    UploadType = rt.models.uploads.UploadType
    # Client = rt.models.pcsw.Client
    Client = dd.plugins.clients.client_model

    # create some random uploads, all uploaded by hubert
    if not dd.plugins.clients.demo_coach:
        return
    ar = rt.login(dd.plugins.clients.demo_coach)
    # user = ar.get_user()
    # CLIENTS = Cycler(rt.models.pcsw.CoachedClients.request(user=hubert))
    # CLIENTS = Cycler(Client.get_clients_coached_by(user))
    CLIENTS = Cycler(Client.objects.all())
    if len(CLIENTS) == 0:
        # raise Exception("{} has no clients?!".format(user))
        raise Exception("No clients?!")
    UPLOAD_TYPES = Cycler(UploadType.objects.all())
    for i in range(5):
        cli = CLIENTS.pop()
        for j in range(2):
            obj = Upload(
                project=cli,
                owner=cli,
                # user=hubert,
                end_date=settings.SITE.demo_date(360+i*10),
                type=UPLOAD_TYPES.pop())
            obj.on_create(ar)  # sets `user` and `needed`
            yield obj
