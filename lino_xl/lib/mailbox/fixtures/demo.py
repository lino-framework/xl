from unipath import Path
from lino.api import dd, rt
from lino_xl.lib.mailbox.models import get_new_mail
def objects():
    Mailbox = rt.models.django_mailbox.Mailbox
    mp = rt.settings.SITE.cache_dir.child("media", "mailbox")
    rt.settings.SITE.makedirs_if_missing(mp)
    dd.logger.info("Mailbox path is %s", mp)
    
    for (protocol, name, origin) in dd.plugins.mailbox.mailbox_templates:
        filename = mp.child(name)
        origin.copy(filename)
        yield Mailbox(
            name=name,
            uri=protocol + "://" + filename)

    name = 'team.mbox'
    origin = Path(__file__).parent.child(name)
    filename = mp.child(name)
    origin.copy(filename)
    mbx = Mailbox(name=name, uri="mbox://" + filename)
    yield mbx
    get_new_mail()
