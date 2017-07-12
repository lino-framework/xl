from lino.api import rt, _
from lino.utils.mldbc import babeld

def objects():
    Account = rt.models.ana.Account
    Group = rt.models.ana.Group
    
    def x(ref, name):
        if len(ref) == 4:
            kwargs = dict(ref=ref)
            ref = ref[:-1]
            while len(ref):
                try:
                    grp = Group.get_by_ref(ref)
                    kwargs.update(group=grp)
                    break
                except Group.DoesNotExist:
                    pass
                ref = ref[:-1]
            return babeld(Account, name, **kwargs)
        else:
            return babeld(Group, name, ref=ref)
        
    yield x("1", _("Operation costs"))
    yield x("1100", _("Wages"))
    yield x("1200", _("Transport"))
    yield x("1300", _("Training"))
    yield x("1400", _("Other costs"))
    
    yield x("2", _("Administrative costs"))
    yield x("2100", _("Secretary wages"))
    yield x("2110", _("Manager wages"))
    yield x("2200", _("Transport"))
    yield x("2300", _("Training"))
    
    yield x("3", _("Investments"))
    yield x("3000", _("Investment"))
    
    yield x("4", _("Project 1"))
    yield x("4100", _("Wages"))
    yield x("4200", _("Transport"))
    yield x("4300", _("Training"))
    
    yield x("5", _("Project 2"))
    yield x("5100", _("Wages"))
    yield x("5200", _("Transport"))
    yield x("5300", _("Other costs"))
