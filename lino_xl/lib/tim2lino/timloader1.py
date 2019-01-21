# -*- coding: UTF-8 -*-
# Copyright 2009-2017 Rumma & Ko Ltd
# License: BSD (see file COPYING for details)

"""Import legacy data from TIM (basic version).

Usage:

- :attr:`legacy_data_path <lino.core.site.Site.legacy_data_path>` must
  point to the TIM data path, e.g.::

      legacy_data_path = '~/vbshared2/drives/L/backup/data/privat'

- Add ``'tim2lino'`` to your
  :attr:`demo_fixtures <lino.core.site.Site.demo_fixtures>`.

- Run :manage:`prep`.

"""
from __future__ import unicode_literals

GET_THEM_ALL = True

START_YEAR = 2002
"""
Don't import vouchers before 2002. TODO: make this
configurable
"""

import datetime
from decimal import Decimal
# from lino.utils.quantities import Duration

from dateutil import parser as dateparser

from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.timezone import make_aware

from lino.utils import dblogger
from lino.utils import dpy
from lino.mixins import Created

from lino_xl.lib.sheets.choicelists import CommonItems
from lino_xl.lib.ledger.utils import ZERO

from lino.core.utils import obj2str
from lino.core.utils import is_valid_email

from lino_xl.lib.ledger.utils import myround
from lino_xl.lib.tim2lino.utils import TimLoader

from lino.api import dd, rt

# Activity = dd.resolve_model('pcsw.Activity')
Country = dd.resolve_model('countries.Country')
Place = dd.resolve_model('countries.Place')
Person = dd.resolve_model("contacts.Person")
Company = dd.resolve_model("contacts.Company")
Account = rt.models.ledger.Account
# Group = dd.resolve_model('accounts.Group')
Journal = dd.resolve_model('ledger.Journal')
Movement = dd.resolve_model('ledger.Movement')
# potentially UnresolvedModel:
Household = dd.resolve_model('households.Household')
List = dd.resolve_model('lists.List')

if True:
    users = dd.resolve_app('users')
    households = dd.resolve_app('households')
    vat = dd.resolve_app('vat')
    sales = dd.resolve_app('sales')
    ledger = dd.resolve_app('ledger')
    products = dd.resolve_app('products')
    contacts = dd.resolve_app('contacts')
    finan = dd.resolve_app('finan')
    sepa = dd.resolve_app('sepa')
    lists = dd.resolve_app('lists')

# if dd.is_installed('vat'):    
#     VatRule = rt.models.vat.VatRule


# def convert_username(name):
    # return name.lower()

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


def vat_regime(idreg):
    if idreg == 'A':
        return VatRegimes.subject
    elif idreg == 'P':
        return VatRegimes.private
    elif idreg == 'C':
        return VatRegimes.cocontractor
    elif idreg == 'I':
        return VatRegimes.intracom
    elif idreg == 'S':
        return VatRegimes.intracom
    elif idreg == 'X':
        return VatRegimes.outside
    elif idreg == '0':
        return VatRegimes.exempt
    elif idreg == 'D':
        return VatRegimes.de
    elif idreg == 'L':
        return VatRegimes.lu


def pcmn2type(idgen):
    if idgen[0] == '6':
        return CommonItems.expenses
    if idgen[0] == '7':
        return CommonItems.incomes
    if idgen[0] == '4':
        return CommonItems.liabilities
    return CommonItems.assets


def tim2bool(x):
    if not x.strip():
        return False
    return True


def convert_gender(v):
    if v in ('W', 'F'):
        return 'F'
    if v == 'M':
        return 'M'
    return None


def mton(s, default=None):  # PriceField
    s = s.strip()
    if not s:
        return default
    if s != "GRATIS":
        # TIM accepted an (erroneous) amount '36535..23' as 36535
        # (omitting the part after the duplicated ".")
        i = s.find('..')
        if i != -1:
            s = s[:i]
        return myround(Decimal(s))
    return Decimal()


def qton(s):  # QuantityField
    return s.strip()
    # s = s.strip()
    # if s:
        # if ':' in s: return Duration(s)
        # if s.endswith('%'):
            # return Decimal(s[:-1]) / 100
        # return Decimal(s)
    # return None


def isolang(x):
    if x == 'K':
        return 'et'
    if x == 'E':
        return 'en'
    if x == 'D':
        return 'de'
    if x == 'F':
        return 'fr'
    # if x == 'N' : return 'nl'


def store_date(row, obj, rowattr, objattr):
    v = row[rowattr]
    if v:
        if isinstance(v, basestring):
            v = dateparser.parse(v)
        setattr(obj, objattr, v)


def year_num(iddoc):
    # TODO: handle data before A.D. 2000
    iyear = 2000 + int(iddoc[:2])
    if iyear < START_YEAR:
        return (None, None)
    year = ledger.FiscalYear.from_int(iyear, None)
    if year is None:  # added 20190121
        year = ledger.FiscalYear.create_from_year(iyear)
        year.full_clean()
        year.save()
    num = int(iddoc[2:])
    return (year, num)


def row2jnl(row):
    try:
        jnl = Journal.objects.get(ref=row.idjnl.strip())
    except Journal.DoesNotExist:
        return None, None, None
    year, num = year_num(row.iddoc)
    # if year < 2002:
    #     # Don't import vouchers before 2002. TODO: make this
    #     # configurable
    #     return None, None, None
    return jnl, year, num


# def country2kw(row,kw):


def try_full_clean(i):
    while True:
        try:
            i.full_clean()
        except ValidationError as e:
            if not hasattr(e, 'message_dict'):
                raise
            for k in e.message_dict.keys():
                fld = i._meta.get_field(k)
                v = getattr(i, k)
                setattr(i, k, fld.default)
                dblogger.warning(
                    "%s : ignoring value %r for %s : %s",
                    obj2str(i), v, k, e)
        return


class TimLoader(TimLoader):

    sales_gen2art = dict()
    """A dict which maps a `GEN->IdGen` to a product instance or id.
    
    """

    def get_customer(self, pk):
        pk = pk.strip()
        if not pk:
            return None
        pk = self.par_pk(pk)
        try:
            return contacts.Partner.objects.get(pk=pk)
        except contacts.Partner.DoesNotExist:
            return None

    def par_pk(self, pk):
        if pk.startswith('T'):
            return 3000 + int(pk[1:]) - 256
        else:
            return int(pk)

    def store(self, kw, **d):
        for k, v in d.items():
            if v is not None:
                if isinstance(v, basestring):
                    v = self.decode_string(v).strip()
            # if v:
                kw[k] = v

    def short2iso(self, s):
        if s == 'B':
            return 'BE'
        if s == 'D':
            return 'DE'
        if s == 'F':
            return 'FR'
        if s == 'L':
            return 'LU'
        if s == 'E':
            return 'ES'
        if s == 'H':
            return 'HU'
        if s == 'I':
            return 'IT'
        if s == 'USA':
            return 'US'
        if s == 'A':
            return 'AT'
        if s == 'AUS':
            return 'AU'
        if s == 'BEN':
            return 'BJ'
        if s == 'ANG':
            return 'AO'
        if s == 'TUN':
            return 'TN'
        if s == 'EST':
            return 'EE'
        if s == 'SLO':
            return 'SK'
        if s == 'S':
            return 'SE'
        if s == 'D-':
            return 'DE'
        if s == 'COL':
            return 'CO'
        if s == 'CAM':
            return 'CM'
        if s == 'SF':
            return 'FI'
        if s == 'VIE':
            return ''
        if s == 'BRA':
            return 'BR'
        return s
        # if s == 'AU': return 'AU'
        # if s == 'NL': return 'NL'
        # raise Exception("Unknown short country code %r" % s)

    def load_gen2group(self, row, **kw):
        idgen = row.idgen.strip()
        if not idgen:
            return
        if len(idgen) < self.LEN_IDGEN:
            # dclsel = row.dclsel.strip()
            kw.update(ref=idgen)
            # if dd.is_installed('sheets'):
            #     kw.update(sheet_item=pcmn2type(idgen))
            self.babel2kw('libell', 'name', row, kw)
            # def names2kw(kw,*names):
                # names = [n.strip() for n in names]
                # kw.update(name=names[0])
            # names2kw(kw,row.libell1,row.libell2,row.libell3,row.libell4)
            """TIM accepts empty GEN->Libell fields. In that 
            case we take the ref as name.
            """
            # kw.setdefault('name', idgen)
            # ag = accounts.Group(**kw)
            # self.GROUPS[idgen] = ag
            # yield ag

    def load_gen2account(self, row, **kw):
        idgen = row.idgen.strip()
        if not idgen:
            return
        if len(idgen) == self.LEN_IDGEN:
            # ag = None
            # for length in range(len(idgen), 0, -1):
            #     # print idgen[:length]
            #     ag = self.GROUPS.get(idgen[:length])
            #     if ag is not None:
            #         break
            # dclsel = row.dclsel.strip()
            kw.update(ref=idgen)
            # kw.update(group=ag)
            # if dd.is_installed('sheets'):
            #     kw.update(sheet_item=pcmn2type(idgen))
            self.babel2kw('libell', 'name', row, kw)
            kw.update(purchases_allowed=True)
            kw.update(sales_allowed=True)
            # def names2kw(kw,*names):
                # names = [n.strip() for n in names]
                # kw.update(name=names[0])
            # names2kw(kw,row.libell1,row.libell2,row.libell3,row.libell4)
            obj = Account(**kw)
            # if idgen == "612410":
                # raise Exception(20131116)
            # dblogger.info("20131116 %s",dd.obj2str(obj))
            # dblogger.info("20131116 ACCOUNT %s ",obj)
            yield obj

    def get_account(self, idgen):
        idgen = idgen.strip()
        if not idgen:
            return None
        try:
            return ledger.Account.objects.get(ref=idgen)
        except ledger.Account.DoesNotExist:
            return None
        
    def load_fin(self, row, **kw):
        jnl, year, number = row2jnl(row)
        if jnl is None:
            dblogger.info("No journal %s (%s)", row.idjnl, row)
            return
        if year < START_YEAR:
            return
        kw.update(year=year)
        kw.update(number=number)
        # kw.update(id=pk)
        kw.update(entry_date=row.date)
        kw.update(voucher_date=row.date)
        kw.update(user=self.get_user())
        kw.update(balance1=mton(row.mont1, ZERO))
        kw.update(balance2=mton(row.mont2, ZERO))
        doc = jnl.create_voucher(**kw)
        self.FINDICT[(jnl, year, number)] = doc
        # print row.etat
        if row.etat == self.etat_registered:
            self.must_register.append(doc)
        return doc

    def load_fnl(self, row, **kw):
        jnl, year, number = row2jnl(row)
        if jnl is None:
            dblogger.info("No journal %s (%s)", row.idjnl, row)
            return
        if year < START_YEAR:
            return
        doc = self.FINDICT.get((jnl, year, number))
        if doc is None:
            raise Exception("FNL %r without document" %
                            list(jnl, year, number))
        try:
            kw.update(seqno=int(row.line.strip()))
        except ValueError:
            pass  # some lines contain "***"
        if row.date:
            kw.update(date=row.date)
        try:
            if row.idctr == ('V'):
                kw.update(partner_id=self.par_pk(row.idcpt.strip()))
                kw.update(
                    account=vat.TradeTypes.sales.get_main_account())
            elif row.idctr == ('E'):
                kw.update(partner_id=self.par_pk(row.idcpt.strip()))
                kw.update(
                    account=vat.TradeTypes.purchases.get_main_account())
            elif row.idctr == ('G'):
                kw.update(partner_id=self.par_pk(row.idcpt.strip()))
                kw.update(
                    account=vat.TradeTypes.wages.get_main_account())
            elif row.idctr == ('S'):
                kw.update(partner_id=self.par_pk(row.idcpt.strip()))
                kw.update(
                    account=vat.TradeTypes.clearings.get_main_account())
            else:
                a = Account.objects.get(ref=row.idcpt.strip())
                kw.update(account=a)
            kw.update(amount=mton(row.mont, ZERO))
            kw.update(dc=self.dc2lino(row.dc))
        except Exception as e:
            dblogger.warning(
                "Failed to load FNL line %s from %s : %s", row, kw, e)
            raise
        try:
            kw.update(match=row.match.strip())
            item = doc.add_voucher_item(**kw)
            # match = row.match.strip()
            # if match:
            #     lst = self.must_match.setdefault(match, [])
            #     lst.append((doc, item))
            #     # self.must_match.append((doc, item, match))
            return item
        except Exception as e:
            dblogger.warning(
                "Failed to load FNL line %s from %s : %s", row, kw, e)

    def load_ven(self, row, **kw):
        jnl, year, number = row2jnl(row)
        if jnl is None:
            dblogger.info("No journal %s (%s)", row.idjnl, row)
            return
        if year < START_YEAR:
            dblogger.info("Ignore %s %s because year %s <%s", row.idjnl, number, year, START_YEAR)
            return
        kw.update(year=year)
        kw.update(number=number)
        kw.update(vat_regime=vat_regime(row.idreg.strip()))
        # kw.update(id=pk)
        partner = self.get_customer(row.idpar)
        if partner is None:
            raise Exception("No partner id {0} in {1}".format(row.idpar, row))
        else:
            kw.update(partner=partner)
        if jnl.trade_type.name == 'sales':
            # kw.update(imode=self.DIM)
            if row.idprj.strip():
                kw.update(project_id=int(row.idprj.strip()))
            kw.update(discount=mton(row.remise))
        elif jnl.trade_type.name == 'purchases':
            pass
            # kw.update(partner=contacts.Partner.objects.get(
            #     pk=self.par_pk(row.idpar)))
            # partner=contacts.Partner.objects.get(pk=self.par_pk(row.idpar))
        else:
            raise Exception("Unknown TradeType %r" % jnl.trade_type)
        kw.update(entry_date=row.date)
        kw.update(voucher_date=row.date)
        kw.update(user=self.get_user(row.auteur))
        kw.update(total_excl=mton(row.montr))
        kw.update(total_vat=mton(row.montt))
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
        if jnl is None:
            return
        if year < START_YEAR:
            return
        doc = self.VENDICT.get((jnl, year, number))
        if doc is None:
            msg = "VNL {0} without document".format(
                [jnl.ref, year, number])
            dblogger.warning(msg)
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
        idart = row.idart.strip()
        if isinstance(doc, sales.VatProductInvoice):
            if row.code in ('A', 'F'):
                kw.update(product=products.Product.get_by_ref(idart))
            elif row.code == 'G':
                a = self.vnlg2product(row)
                if a is not None:
                    kw.update(product=a)
            try:
                kw.update(unit_price=mton(row.prixu))
            except Exception:
                msg = "VNL {} ignore invalid unit_price {}".format(
                    [jnl.ref, year.ref, number], row.prixu)
                dblogger.warning(msg)
            qty = qton(row.qte)
            # fld = doc.items.model._meta.get_field('qty')
            qty_fld = sales.InvoiceItem._meta.get_field('qty')
            try:
                qty = qty_fld.to_python(qty)
                kw.update(qty=qty)
            except Exception:
                msg = "VNL {} ignore invalid qty {}".format(
                    [jnl.ref, year.ref, number], qty)
                dblogger.warning(msg)
        elif isinstance(doc, vat.VatAccountInvoice):
            if row.code == 'G':
                kw.update(account=idart)
        kw.update(title=row.desig.strip())
        vc = tax2vat(row.idtax)
        kw.update(vat_class=vc)
        mb = mton(row.cmont)
        mv = mton(row.montt)
        kw.update(total_base=mb)
        kw.update(total_vat=mv)
        if mb is not None and mv is not None:
            kw.update(total_incl=mb+mv)
        # kw.update(qty=row.idtax.strip())
        # kw.update(qty=row.montt.strip())
        # kw.update(qty=row.attrib.strip())
        # kw.update(date=row.date)

        # check whether we need a vat rule
        # if mv and mb:
        #     vatrule = dict(vat_class=vc, vat_regime=doc.vat_regime)
        #     vatrule.update(
        #         country=doc.partner.country or
        #         dd.plugins.countries.get_my_country())
        #     try:
        #         VatRule.objects.get(**vatrule)
        #     except VatRule.DoesNotExist:
        #         vatrule.update(rate=myround(mv / mb))
        #         yield VatRule(**vatrule)
        try:
            yield doc.add_voucher_item(**kw)
        except Exception as e:
            dblogger.warning("Failed to load VNL line %s from %s : %s",
                             row, kw, e)

    def vnlg2product(self, row):
        a = row.idart.strip()
        return self.sales_gen2art.get(a)

    # Countries already exist after initial_data, but their short_code is
    # needed as lookup field for Places.
    def load_nat(self, row):
        if not row['isocode'].strip():
            return
        try:
            country = Country.objects.get(
                isocode=row['isocode'].strip())
        except Country.DoesNotExist:
            country = Country(isocode=row['isocode'].strip())
            country.name = row['name'].strip()
        if row['idnat'].strip():
            country.short_code = row['idnat'].strip()
        return country

    def load_plz(self, row):
        pk = row.pays.strip()
        if not pk:
            return
        name = row.nom.strip() or row.cp.strip()
        if not name:
            return

        if False:  # severe
            country = Country.objects.get(isocode=self.short2iso(pk))
            # country = Country.objects.get(short_code=pk)
        else:
            try:
                country = Country.objects.get(isocode=self.short2iso(pk))
                # country = Country.objects.get(short_code=pk)
            except Country.DoesNotExist:
                dblogger.warning(
                    "Ignored PLZ %s (with invalid country %s)", row, pk)
                return
        zip_code = row['cp'].strip()
        if Place.objects.filter(zip_code=zip_code, country=country).exists():
            dblogger.warning(
                "Ignored PLZ %s (duplicate zip code %s-%s)",
                row, country.isocode, zip_code)
            return

        kw = dict(
            zip_code=zip_code,
            name=name,
            country=country,
        )
        return Place(**kw)

    def load_par(self, row):
        kw = {}
        # kw.update(
        #     street2kw(join_words(
        #         row['RUE'],
        #         row['RUENUM'],
        #         row['RUEBTE'])))

        # the following code needs the top-level (possibly abstract)
        # models:
        from lino_xl.lib.contacts.models import Person, Company
        partner_models = (Person, Company)
        if dd.is_installed('households'):
            from lino_xl.lib.households.models import Household
            partner_models = (Person, Company, Household)

        self.store(kw, id=self.par_pk(row.idpar))

        cl = self.par_class(row)
        
        if cl is None:
            dblogger.warning(
                "Ignored PAR record %s (IdPrt %r)" % (
                    row.idpar, row.idprt))
            return
        
        if issubclass(cl, partner_models):
            email = row.email.strip()
            if email and is_valid_email(email):
                self.store(kw, email=email)

        # if 'idreg' in row:
        if row.idreg:
            self.store(kw, vat_regime=vat_regime(row.idreg.strip()))
            
        # if 'idgen' in row:
        if row.idgen:
            self.store(kw, purchase_account=self.get_account(row.idgen))
            
        if issubclass(cl, Company):
            # cl = Company
            self.store(
                kw,
                prefix=row['allo'].strip(),
                name=row.firme.strip() + ' ' + row.vorname,
            )
            if dd.is_installed('vat'):
                self.store(
                    kw, vat_id=row['notva'].strip())
                
        if issubclass(cl, Person):
            # self.store(kw, prefix=row.allo)
            # kw.update(**name2kw(self.decode_string(row.firme)))
            last_name = row.firme.strip()
            if row.name2.strip():
                last_name += '-' + row.name2.strip()
            self.store(
                kw,
                first_name=row['vorname'].strip(),
                last_name=last_name,
                # birth_date=row['gebdat'],
                title=row['allo'].strip(),
            )
            assert kw['first_name'] or kw['last_name']
            # depends on which dbf module is being used:
            # if 'sex' in row:
            if hasattr(row, 'sex'):
                # sex = row.get('sex', None)
                sex = row.sex
                self.store(
                    kw, gender=convert_gender(sex))
        if dd.is_installed('households'):
            if issubclass(cl, Household):
                self.store(
                    kw,name=row.firme.strip() + ' ' + row.vorname.strip())
        if dd.is_installed('lists') and issubclass(cl, List):
            self.store(kw, designation=row.firme)
        
        if issubclass(cl, Created):
            if 'datcrea' in row:
                created = row.get('datcrea', None)
                if created:
                    created = datetime.datetime.combine(
                        created, datetime.time(0, 0, 0))
                    if settings.USE_TZ:
                        created = make_aware(created)
                    kw.update(created=created)

        # if cl is not List:
        if issubclass(cl, rt.models.contacts.Partner):
            language = isolang(row['langue'])
            
            if settings.SITE.get_language_info(language):
                self.store(kw, language=language)

            # if 'memo' in row:
            if row.memo:
                self.store(
                    kw, remarks=self.dbfmemo(row.get('memo') or ''))

            isocode = self.short2iso(row.pays.strip())
            if isocode:
                try:
                    country = Country.objects.get(
                        isocode=isocode)
                except Country.DoesNotExist:
                    country = Country(isocode=isocode,
                                      name=isocode)
                    country.save()
                kw.update(country=country)

                zip_code = row['cp'].strip()
                if zip_code:
                    kw.update(zip_code=zip_code)
                    qs = Place.objects.filter(
                        country=country,
                        zip_code__exact=zip_code,
                    )
                    if qs.count() == 0:
                        city = Place(zip_code=zip_code,
                                     name=zip_code,
                                     country=country)
                        city.save()
                        kw.update(city=city)
                    else:
                        kw.update(city=qs[0])
                        s = self.duplicate_zip_codes.get(country, set([]))
                        s.add(zip_code)
                    
            self.store(
                kw,
                phone=row['tel'].strip(),
                fax=row['fax'].strip(),
                street=row['rue'].strip(),
                street_no=row['ruenum'],
                street_box=row['ruebte'].strip(),
            )

            # kw.update(street2kw(join_words(row['RUE'],
            # row['RUENUM'],row['RUEBTE'])))

        try:
            obj = cl(**kw)
        except Exception:
            dblogger.warning("Failed to instantiate %s from %s",
                             cl, kw)
            raise
        yield obj

        def compte2iban(s, **kw):
            a = s.split(':')
            if len(a) == 1:
                kw.update(iban=s)
            elif len(a) == 2:
                kw.update(bic=a[0])
                kw.update(iban=a[1])
            else:
                kw.update(iban=s)
            return kw

        if not dd.is_installed('sepa'):
            return
        
        compte1 = row['compte1'].strip()
        if compte1:
            obj.full_clean()
            obj.save()
            kw = compte2iban(compte1, partner=obj, primary=True)
            if kw['iban']:
                obj = sepa.Account(**kw)
                try:
                    obj.full_clean()
                    yield obj
                except ValidationError:
                    dblogger.warning(
                        "Ignored invalid PAR->Compte1 %r", compte1)

    def load_prj(self, row, **kw):
        pk = int(row.idprj.strip())
        kw.update(id=pk)
        if row.parent.strip():
            kw.update(parent_id=int(row.parent))
        kw.update(name=row.name1.strip())
        # if row.idpar.strip():
        #     kw.update(partner_id=self.par_pk(row.idpar.strip()))

        kw.update(ref=row.seq.strip())
        # kw.update(user=self.get_user(None))
        desc = self.dbfmemo(row.abstract).strip() + '\n\n' + self.dbfmemo(row.body)
        # kw.update(summary=self.dbfmemo(row.abstract))
        kw.update(description=desc)
        return tickets.Project(**kw)

    def load_pin(self, row, **kw):
        pk = int(row.idpin)
        kw.update(id=pk)
        if row.idprj.strip():
            kw.update(project_id=int(row.idprj))
            # kw.update(partner_id=PRJPAR.get(int(row.idprj),None))
        kw.update(summary=row.short.strip())
        kw.update(description=self.dbfmemo(row.memo))
        kw.update(state=ticket_state(row.idpns))
        kw.update(closed=row.closed)
        kw.update(created=row['date'])
        kw.update(modified=datetime.datetime.now())
        kw.update(reporter=self.get_user(row.idusr))
        return tickets.Ticket(**kw)
        # if row.idpar.strip():
        #     kw = dict(project=obj)
        #     kw.update(partner_id=self.par_pk(row.idpar))
        #     yield tickets.Sponsorship(**kw)

    def load_art(self, row, **kw):
        # try:
        #     pk = int(row.idart)
        # except ValueError as e:
        #     dblogger.warning("Ignored %s: %s", row, e)
        #     # return
        idart = row.idart.strip()
        if not idart:
            dblogger.warning("Ignored %s: ART->IdArt is empty", row)
            return
        kw.update(ref=idart)
        # if pk == 0:
        #     pk = 1000  # mysql doesn't accept value 0
        # kw.update(id=pk)
        self.babel2kw('name', 'name', row, kw)
        # dblogger.info("20140823 product %s", kw)
        kw.setdefault('name', idart)
        return products.Product(**kw)

    def create_users(self):

        self.ROOT = users.User(
            username='tim', first_name='tim', 
            id=1,
            user_type=users.UserTypes.admin)
        self.ROOT.set_password("1234")
        # if isinstance(self.ROOT, rt.models.contacts.Partner):
        #     self.ROOT.name = "tim"
        yield self.ROOT

    def get_user(self, idusr=None):
        return self.ROOT

    def objects(tim):

        self = tim
        
        yield self.create_users()

        # settings.SITE.loading_from_dump = True

        if False:
            self.DIM = sales.InvoicingMode(name='Default')
            yield self.DIM

        # yield sales.Invoice.create_journal('sales',
        #    chart=self.CHART,name="Verkaufsrechnungen",ref="VKR")
        # yield ledger.AccountInvoice.create_journal('purchases',
        #    chart=self.CHART,name="Einkaufsrechnungen",ref="EKR")
        # from lino.modlib.users import models as users
        # ROOT = users.User.objects.get(username='root')
        # DIM = sales.InvoicingMode.objects.get(name='Default')
        # yield tim.load_dbf('GEN', self.load_gen2group)
        yield tim.load_dbf('GEN', self.load_gen2account)

        yield dpy.FlushDeferredObjects

        self.after_gen_load()

        yield tim.load_dbf('ART')
        yield tim.load_dbf('JNL')

        yield dpy.FlushDeferredObjects

        # yield tim.load_dbf('NAT')
        yield tim.load_dbf('PLZ')
        yield tim.load_dbf('PAR')

        # from lino_xl.lib.vat.fixtures import euvatrates
        # yield euvatrates.objects()

        if False:
            settings.SITE.loading_from_dump = True
            yield tim.load_dbf('PRJ')
            yield dpy.FlushDeferredObjects
            settings.SITE.loading_from_dump = False

        if True:  # GET_THEM_ALL:

            yield tim.load_dbf('VEN')
            yield tim.load_dbf('VNL')

            yield tim.load_dbf('FIN')
            yield tim.load_dbf('FNL')

