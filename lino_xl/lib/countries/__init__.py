# Copyright 2008-2019 Rumma & Ko Ltd
# License: GNU Affero General Public License v3 (see file COPYING for details)

"""See :doc:`/specs/countries`.

.. autosummary::
   :toctree:

    utils
    fixtures

"""

from lino.api import ad, _


class Plugin(ad.Plugin):
    "The countries plugin."

    verbose_name = _("Places")
    needs_plugins = ['lino.modlib.office', 'lino_xl.lib.xl']

    # settings:

    hide_region = False
    """Whether to hide the `region` field in postal addresses.  Set this
    to `True` if you live in a country like Belgium.  Belgium is
    --despite their constant language disputes-- obviously a very
    united country since they don't need a `region` field when
    entering a postal address.  In Belgium, when you write a letter,
    you just say the zip code and name of the city.  In many other
    countries there is a mandatory intermediate field.

    """

    region_label = _("County")
    """The verbose_name of the region field."""

    country_code = 'BE'
    """The 2-letter ISO code of the country where the site owner is
    located.  This may not be empty, and there must be a country with
    that ISO code in :class:`lino_xl.lib.countries.models.Country`.

    """

    municipality_type = '50'
    """The place type to be considered as administrativ municipality.

    See :attr:`lino_xl.lib.courses.CountryCity.municipality`

    """

    def before_analyze(self):
        super(Plugin, self).before_analyze()
        from lino_xl.lib.countries.mixins import AddressLocation
        from lino.core.utils import models_by_base
        if self.hide_region:
            for m in models_by_base(AddressLocation):
                m.hide_elements('region')

    def on_site_startup(self, site):
        if self.country_code is None:
            raise Exception(
                "countries plugin requires a nonempty `country_code` setting.")

    def setup_config_menu(self, site, user_type, m):
        m = m.add_menu(self.app_label, self.verbose_name)
        m.add_action('countries.Countries')
        m.add_action('countries.Places')

    def get_my_country(self):
        """Return the :class:`Country` instance configured by
:attr:`country_code`."""
        Country = self.site.models.countries.Country
        try:
            return Country.objects.get(pk=self.country_code)
        except Country.DoesNotExist:
            return
