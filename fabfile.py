from atelier.fablib import *
setup_from_fabfile(globals(), 'lino_xl')

env.languages = "en de fr et nl pt-br es".split()
env.tolerate_sphinx_warnings = False
env.cleanable_files = ['docs/api/lino_xl.*']

env.locale_dir = 'lino_xl/lib/xl/locale'

add_demo_project('lino_xl.projects.max.settings.demo')
add_demo_project('lino_xl.projects.i18n.settings')
add_demo_project('lino_xl.projects.min1.settings.demo')
add_demo_project('lino_xl.projects.min2.settings.demo')

env.revision_control_system = 'git'
