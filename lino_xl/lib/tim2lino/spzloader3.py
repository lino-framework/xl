# -*- coding: UTF-8 -*-
# Copyright 2018 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""
Import legacy data from TIM (third step). 

Much legacy data is already in Lino: first imported by
:mod:`spzloader`, then manually reviewed and maintained, then we
imported the legacy database once more, adding calendar entries and
more data about partners.

This third loader additionally imports the 2018 sales invoices from
TIM to Lino.

In the project direcory on their production server I have a script
:file:`tl3.py`::

    from lino_xl.lib.tim2lino.spzloader3 import TimLoader
    TimLoader.run()

That script runs for quite some time. So I invoke it using nohup to
avoid having it killed when my terminal closes::

    $ nohup python manage.py run tl3.py &
    [1] 18804
    $ nohup: ignoring input and appending output to ‘nohup.out’

I can then watch the :xfile:`lino.log` while the script is running.

And when the script has finished, I can see the results in the
:xfile:`nohup.out` file and in :xfile:`lino.log`.
"""
from __future__ import unicode_literals
from builtins import str

import datetime
from dateutil import parser as dateparser

from django.core.exceptions import ValidationError
from django.db import DEFAULT_DB_ALIAS

# from lino.utils import mti
from lino.utils.instantiator import create_row
from lino.utils.instantiator import create
from lino.utils.mti import mtichild, insert_child
from lino.core.gfks import gfk2lookup

from lino.api import dd, rt, _


from .spzloader import TimLoader
from .timloader1 import row2jnl, mton, qton

Person = dd.resolve_model("contacts.Person")
# Company = dd.resolve_model("contacts.Company")
RoleType = dd.resolve_model("contacts.RoleType")
Role = dd.resolve_model("contacts.Role")
Household = rt.models.households.Household
Product = dd.resolve_model('products.Product')
# List = dd.resolve_model('lists.List')
Client = rt.models.tera.Client
ClientContact = rt.models.clients.ClientContact
Course = rt.models.courses.Course
Line = rt.models.courses.Line
ActivityLayouts = rt.models.courses.ActivityLayouts
Enrolment = rt.models.courses.Enrolment
EnrolmentStates = rt.models.courses.EnrolmentStates
Country = rt.models.countries.Country
Product = rt.models.products.Product

Invoice = rt.models.sales.VatProductInvoice
InvoiceItem = rt.models.sales.InvoiceItem

Account = dd.resolve_model('ledger.Account')

User = rt.models.users.User
UserTypes = rt.models.users.UserTypes
Partner = rt.models.contacts.Partner
Company = rt.models.contacts.Company
# Coaching = rt.models.coachings.Coaching

Note = rt.models.notes.Note
Guest = rt.models.cal.Guest
GuestStates = rt.models.cal.GuestStates
Event = rt.models.cal.Event
EventType = rt.models.cal.EventType
EntryStates = rt.models.cal.EntryStates
from lino_xl.lib.vat.choicelists import VatClasses, VatRegimes

def tax2vat(idtax):
    idtax = idtax.strip()
    if idtax == 'D20':
        return VatClasses.normal
    elif idtax == 'D18':
        return VatClasses.normal
    elif idtax == '0':
        return VatClasses.exempt
    elif idtax == 'IS':
        return VatClasses.normal
    elif idtax == 'XS':
        return VatClasses.normal
    else:
        return VatClasses.normal
    raise Exception("Unknown VNl->IdTax %r" % idtax)


class TimLoader(TimLoader):

    # archived_tables = set('GEN ART VEN VNL JNL FIN FNL'.split())
    # archive_name = 'rumma'
    # has_projects = False
    # languages = 'de fr'
    etat_registered = "C"
    # etat_registered = "¹"
    
    def __init__(self, *args, **kwargs):
        super(TimLoader, self).__init__(*args, **kwargs)
        Line = rt.models.courses.Line
        Team = rt.models.teams.Team
        # Country = rt.models.countries.Country
        self.eupen = Team.objects.get(name="Eupen")
        self.stvith = Team.objects.get(name="St. Vith")

        Line = rt.models.courses.Line
        self.other_groups = Line.objects.filter(
            course_area=ActivityLayouts.default).order_by('id')[0]

        self.ROOT = User.objects.get(username='luc')
        
        
    def par_class(self, data):
        prt = data.idprt
        if prt == 'L':  # Lieferant
            return Company
        elif prt == 'K':  # Krankenkasse
            return Company
        elif prt == 'S':  # Sonstige
            return Company
        elif prt == 'W':  # Netzwerkpartner
            return Company
        elif prt == 'R':  # Ärzte
            return Person
        elif prt == 'Z':  # Zahler
            return Company
        elif prt == 'P':  # Personen
            return Client
        elif prt == 'G':  # Lebensgruppen
            return Household
        elif prt == 'T':  # Therapeutische Gruppen
            return # Household  # List
        #~ dblogger.warning("Unhandled PAR->IdPrt %r",prt)

    def par_pk(self, pk):
        try:
            if pk.startswith('E'):
                return 1000000 + int(pk[1:])
            elif pk.startswith('S'):
                return 2000000 + int(pk[1:])
            return int(pk)
        except ValueError:
            return None

    def get_partner(self, model, idpar):
        pk = self.par_pk(idpar.strip())
        if pk is None:
            return None
        try:
            return model.objects.get(pk=pk)
        except model.DoesNotExist:
            return None

    def load_ven(self, row, **kw):
        jnl, year, number = row2jnl(row)
        if jnl is None:
            dd.logger.info("No journal %s (%s)", row.idjnl, row)
            return
        if year is None or year.ref != '2018':
            # dd.logger.info("Ignoring row before 2018 (%s, %s)", year, jnl)
            return
        if jnl.trade_type.name != 'sales':
            return
        kw.update(year=year)
        kw.update(number=number)
        kw.update(vat_regime=VatRegimes.normal)
        # kw.update(id=pk)

        # reduce to first partner using the Course.ref which contains
        # the old partner id:
        course = Course.get_by_ref(row.idpar.strip(), None)
        if course and course.partner:
            partner = course.partner
        else:
            partner = self.get_partner(Partner, row.idpar)
            if partner is None:
                raise Exception("No partner id {0}".format(row.idpar))
        kw.update(partner=partner)
        # if row.idprj.strip():
        #     kw.update(project_id=int(row.idprj.strip()))
        # kw.update(discount=mton(row.remise))
        kw.update(entry_date=row.date)
        kw.update(voucher_date=row.date)
        kw.update(user=self.get_user(row.auteur))
        kw.update(total_excl=mton(row.mont))
        # kw.update(total_vat=mton(row.montt))
        kw.update(match=row.match.strip())
        doc = jnl.create_voucher(**kw)
        # doc.partner = partner
        # doc.full_clean()
        # doc.save()
        self.VENDICT[(jnl, year, number)] = doc
        if row.etat == self.etat_registered:
            self.must_register.append(doc)
        # match = row.match.strip()
        # if match:
        #     lst = self.must_match.setdefault(match, [])
        #     lst.append((doc, doc))
        #     # self.must_match.append((doc, doc, match))
        return doc

    def load_vnl(self, row, **kw):
        jnl, year, number = row2jnl(row)
        if year is None or year.ref != '2018':
            return
        if jnl is None:
            dd.logger.info("No journal %s (%s)", row.idjnl, row)
            return
        if jnl.trade_type.name != 'sales':
            return
        doc = self.VENDICT.get((jnl, year, number))
        if doc is None:
            msg = "VNL {0} without document".format(
                [jnl.ref, year, number])
            dd.logger.warning(msg)
            return
            # raise Exception(msg)
        # dblogger.info("20131116 %s %s",row.idjnl,row.iddoc)
        # doc = jnl.get_document(year,number)
        # try:
            # doc = jnl.get_document(year,number)
        # except Exception,e:
            # dblogger.warning(str(e))
            # return
        # kw.update(document=doc)
        kw.update(seqno=int(row.line.strip()))
        if row.code in ('A', 'F'):
            idart = row.idart.strip()
            if idart == "*":
                prod = Product.objects.get(pk=2)
            else:
                try:
                    prod = Product.objects.get(pk=idart)
                except Product.DoesNotExist:
                    prod = Product(pk=idart, name=idart)
                    yield prod
            kw.update(product=prod)
        kw.update(unit_price=mton(row.prixu))
        kw.update(qty=qton(row.qte))
        kw.update(title=row.desig.strip())
        # vc = tax2vat(row.idtax)
        # kw.update(vat_class=vc)
        mb = mton(row.cmont)
        # mv = mton(row.montt)
        kw.update(total_base=mb)
        kw.update(total_incl=mb)
        # kw.update(total_vat=mv)
        # if mb is not None and mv is not None:
        #     kw.update(total_incl=mb+mv)
        try:
            yield doc.add_voucher_item(**kw)
        except Exception as e:
            dd.logger.warning("Failed to load VNL %s from %s : %s",
                              row, kw, e)

        
    
    def objects(self):
        
        def bulkdel(qs):
            qs._raw_delete(DEFAULT_DB_ALIAS)
            
        bulkdel(InvoiceItem.objects.filter(
            voucher__accounting_period__ref__startswith="2018"))
        bulkdel(Invoice.objects.filter(
            accounting_period__ref__startswith="2018"))
       
        yield self.load_dbf('VEN')
        yield self.load_dbf('VNL')
