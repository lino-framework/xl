# -*- coding: UTF-8 -*-
# Copyright 2017 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""

Import legacy data from TIM (including households, ...).
An extension of :mod:`timloader <lino_xl.lib.tim2lino.timloader>`.


"""
from __future__ import unicode_literals
import datetime


from django.conf import settings

from lino.utils import mti
from lino.api import dd, rt

from .timloader1 import TimLoader

Person = dd.resolve_model("contacts.Person")
Company = dd.resolve_model("contacts.Company")
Partner = dd.resolve_model("contacts.Partner")
RoleType = dd.resolve_model("contacts.RoleType")
Role = dd.resolve_model("contacts.Role")
Household = dd.resolve_model('households.Household')
Product = dd.resolve_model('products.Product')
List = dd.resolve_model('lists.List')
Member = dd.resolve_model('lists.Member')
households_Member = dd.resolve_model('households.Member')
Account = dd.resolve_model('ledger.Account')

tickets = dd.resolve_app('tickets')
working = dd.resolve_app('working')

def ticket_state(idpns):
    if idpns == ' ':
        return tickets.TicketStates.new
    if idpns == 'A':
        return tickets.TicketStates.waiting
    if idpns == 'C':
        return tickets.TicketStates.fixed
    if idpns == 'X':
        return tickets.TicketStates.cancelled
    return tickets.TicketStates.new
    # return None  # 20120829 tickets.TicketStates.blank_item



class TimLoader(TimLoader):

    archived_tables = set('GEN ART VEN VNL JNL FIN FNL'.split())
    archive_name = 'rumma'
    languages = 'et en de fr'

    def par_class(self, data):
        # wer eine nationalregisternummer hat ist eine Person, selbst wenn er
        # auch eine MWst-Nummer hat.
        prt = data.idprt
        if prt == 'O':
            return Company
        elif prt == 'L':
            return List
        elif prt == 'P':
            return Person
        elif prt == 'F':
            return Household
        #~ dblogger.warning("Unhandled PAR->IdPrt %r",prt)

    def objects(self):

        MemberRoles = rt.models.households.MemberRoles

        self.household_roles = {
            'VATER': MemberRoles.head,
            'MUTTER': MemberRoles.spouse,
            'KIND': MemberRoles.child,
            'K': MemberRoles.child,
        }

        self.contact_roles = cr = {}
        cr.update(DIR=RoleType.objects.get(pk=2))
        cr.update(A=RoleType.objects.get(pk=3))
        cr.update(SYSADM=RoleType.objects.get(pk=4))

        obj = RoleType(name="TIM user")
        yield obj
        cr.update(TIM=obj)
        obj = RoleType(name="Lino user")
        yield obj
        cr.update(LINO=obj)
        obj = RoleType(name="Board member")
        yield obj
        cr.update(VMKN=obj)
        obj = RoleType(name="Member")
        yield obj
        cr.update(M=obj)

        # self.PROD_617010 = Product(
        #     name="Edasimüük remondikulud",
        #     id=40)
        # yield self.PROD_617010

        # self.sales_gen2art['617010'] = self.PROD_617010

        yield super(TimLoader, self).objects()

        yield self.load_dbf('NEW')
        
        yield self.load_dbf('PLS')
        yield self.load_dbf('MBR')

        # yield self.load_dbf('PIN')
        # yield self.load_dbf('DLS')

    # def after_gen_load(self):
    #     super(TimLoader, self).after_gen_load()
    #     self.PROD_617010.sales_account = Account.objects.get(
    #         ref='617010')
    #     self.PROD_617010.save()

    def load_par(self, row):
        for obj in super(TimLoader, self).load_par(row):
            if isinstance(obj, Partner):
                obj.isikukood = row['regkood'].strip()
                obj.created = row['datcrea']
                obj.modified = datetime.datetime.now()
                bd = row['gebdat'].strip()
                if len(bd) == 8:
                    bd = bd.replace("?", "0")
                    bd = bd.replace("x", "0")
                    bd = bd[0:4] + '-' + bd[4:6] + '-' + bd[6:8]
                    obj.birth_date = bd
            yield obj

    def load_pls(self, row, **kw):
        kw.update(ref=row.idpls.strip())
        kw.update(designation=row.name)
        return List(**kw)

    def load_new(self, row, **kw):
        kw.update(id=row.idnew.strip())
        kw.update(pub_date=row.date)
        kw.update(pub_time=row.time.strip() or None)
        kw.update(title=row.title.strip())
        kw.update(user=self.ROOT)
        body = self.dbfmemo(
            row.abstract.strip() + "\n\n" + row.body.strip())
        body = body.replace("ref PAR:", "person ")
        kw.update(body=body)
        return rt.models.blogs.Entry(**kw)

    def load_mbr(self, row, **kw):
        p1 = self.get_customer(row.idpar)
        if p1 is None:
            dd.logger.debug(
                "Failed to load MBR %s : "
                "No idpar", row)
            return
        p2 = self.get_customer(row.idpar2)

        if p2 is not None:
            if row.idpls.strip() == 'M':
                c1 = mti.get_child(p1, Company)
                c2 = mti.get_child(p2, Company)
                if c1 and c2:
                    if c2.parent is None:
                        c2.parent = c1
                        return c2
            
            contact_role = self.contact_roles.get(row.idpls.strip())
            if contact_role is not None:
                kw = dict()
                p = mti.get_child(p1, Company)
                if p is None:
                    dd.logger.debug(
                        "Failed to load MBR %s : "
                        "idpar is not a company", row)
                    return
                kw.update(company=p)
                p = mti.get_child(p2, Person)
                if p is None:
                    dd.logger.debug(
                        "Failed to load MBR %s : "
                        "idpar2 is not a person", row)
                    return
                kw.update(person=p)
                kw.update(type=contact_role)
                return Role(**kw)

            role = self.household_roles.get(row.idpls.strip())
            if role is not None:
                household = mti.get_child(p1, Household)
                if household is None:
                    dd.logger.debug(
                        "Failed to load MBR %s : "
                        "idpar is not a household", row)
                    return
                person = mti.get_child(p2, Person)
                if person is None:
                    dd.logger.debug(
                        "Failed to load MBR %s : idpar2 is not a person", row)
                    return
                return households_Member(
                    household=household,
                    person=person,
                    role=role)
            dd.logger.debug(
                "Failed to load MBR %s : idpar2 is not empty", row)
            return

        try:
            lst = List.objects.get(ref=row.idpls.strip())
        except List.DoesNotExist:
            dd.logger.debug(
                "Failed to load MBR %s : unknown idpls", row)
            return
        kw.update(list=lst)
        kw.update(remark=row.remarq)
        kw.update(partner=p1)
        return Member(**kw)

    def load_dls(self, row, **kw):
        if not row.iddls.strip():
            return
        if not row.idpin.strip():
            return
        try:
            ticket = tickets.Ticket.objects.get(pk=int(row.idpin))
        except tickets.Ticket.DoesNotExist:
            return
        pk = int(row.iddls)
        kw.update(id=pk)
        kw.update(ticket=ticket)
        # if row.idprj.strip():
        #     kw.update(project_id=int(row.idprj))
            # kw.update(partner_id=PRJPAR.get(int(row.idprj),None))
        # if row.idpar.strip():
        #     kw.update(partner_id=self.par_pk(row.idpar))
        kw.update(summary=row.nb.strip())
        kw.update(start_date=row.date)
        kw.update(user=self.get_user(row.idusr))

        def set_time(kw, fldname, v):
            v = v.strip()
            if not v:
                return
            if v == '24:00':
                v = '0:00'
            kw[fldname] = v

        set_time(kw, 'start_time', row.von)
        set_time(kw, 'end_time', row.bis)
        set_time(kw, 'break_time', row.pause)
        # kw.update(start_time=row.von.strip())
        # kw.update(end_time=row.bis.strip())
        # kw.update(break_time=row.pause.strip())
        # kw.update(is_private=tim2bool(row.isprivat))
        obj = working.Session(**kw)
        # if row.idpar.strip():
            # partner_id = self.par_pk(row.idpar)
            # if obj.project and obj.project.partner \
                # and obj.project.partner.id == partner_id:
                # pass
            # elif obj.ticket and obj.ticket.partner \
                # and obj.ticket.partner.id == partner_id:
                # pass
            # else:
                # ~ dblogger.warning("Lost DLS->IdPar of DLS#%d" % pk)
        yield obj
        if row.memo.strip():
            kw = dict(owner=obj)
            kw.update(body=self.dbfmemo(row.memo))
            kw.update(user=obj.user)
            kw.update(date=obj.start_date)
            yield rt.models.notes.Note(**kw)

