from atelier.fablib import *
setup_from_fabfile(globals(), 'lino_xl')

env.languages = "en de fr et nl pt-br es".split()
env.tolerate_sphinx_warnings = True

# caution: ``bs3`` uses the same database file as the first. And then,
# bs3 has :attr:`default_user<lino.core.site.Site.default_user>` set
# to 'anonymous'. Which causes it to deactivate both authentication
# and sessions.
add_demo_project('lino_xl.projects.i18n.settings')
# no longer used:
# add_demo_project('lino_noi.projects.public.settings.demo')

env.revision_control_system = 'git'
