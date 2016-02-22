import sys
from unipath import Path

from lino.utils.pythontest import TestCase
from lino_xl import SETUP_INFO
from lino import PYAFTER26


class LinoTestCase(TestCase):
    django_settings_module = "lino_xl.projects.max.settings.demo"
    project_root = Path(__file__).parent.parent


class PackagesTests(LinoTestCase):
    def test_01(self):
        self.run_packages_test(SETUP_INFO['packages'])


class LibTests(LinoTestCase):

    # def test_users(self):
    #     self.run_simple_doctests("docs/dev/users.rst")

    def test_cal_utils(self):
        self.run_simple_doctests('lino_xl/lib/cal/utils.py')


class SpecsTests(LinoTestCase):

    def test_printing(self):
        self.run_simple_doctests('docs/specs/printing.rst')

    def test_holidays(self):
        self.run_simple_doctests('docs/specs/holidays.rst')

    def test_cv(self):
        self.run_simple_doctests('docs/specs/cv.rst')

    def test_households(self):
        self.run_simple_doctests('docs/specs/households.rst')

    def test_tinymce(self):
        self.run_simple_doctests("docs/specs/tinymce.rst")

    def test_min1(self):
        self.run_simple_doctests("docs/specs/export_excel.rst")


class UtilsTests(LinoTestCase):

    def test_cal(self):
        self.run_simple_doctests("lino_xl/lib/cal/utils.py")


class ProjectsTests(LinoTestCase):
    
    def test_min1(self):
        self.run_django_manage_test("lino_xl/projects/min1")

    def test_min2(self):
        self.run_django_manage_test("lino_xl/projects/min2")


from . import test_appy_pod
