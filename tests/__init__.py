import sys
from unipath import Path

from lino.utils.pythontest import TestCase
from lino_xl import SETUP_INFO
from lino import PYAFTER26


class LinoTestCase(TestCase):
    django_settings_module = "lino.projects.std.settings_test"
    project_root = Path(__file__).parent.parent


class PackagesTests(LinoTestCase):
    def test_01(self):
        self.run_packages_test(SETUP_INFO['packages'])

   
class LibTests(LinoTestCase):

    # def test_users(self):
    #     self.run_simple_doctests("docs/dev/users.rst")

    def test_cal_utils(self):
        self.run_simple_doctests('lino_xl/lib/cal/utils.py')
        
    def test_vat_utils(self):
        self.run_simple_doctests('lino_xl/lib/vat/utils.py')


class UtilsTests(LinoTestCase):

    def test_contacts_utils(self):
        self.run_simple_doctests('lino_xl/lib/contacts/utils.py')


from . import test_appy_pod
