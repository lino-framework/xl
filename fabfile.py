from atelier.fablib import *
setup_from_fabfile(globals(), 'lino_xl')

env.languages = "en de fr et nl pt-br es".split()
env.tolerate_sphinx_warnings = True
env.cleanable_files = ['docs/api/lino_xl.*']

env.locale_dir = 'lino_xl/lib/xl/locale'

add_demo_project('lino_xl.projects.i18n.settings')
add_demo_project('lino_xl.projects.min1.settings')
add_demo_project('lino_xl.projects.min2.settings')

env.revision_control_system = 'git'
