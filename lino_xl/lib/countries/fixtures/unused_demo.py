def objects():
    from lino_xl.lib.countries.fixtures.few_countries import objects
    yield objects()
    from lino_xl.lib.countries.fixtures.few_cities import objects
    yield objects()
