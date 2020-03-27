from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
import os

dependencies = [
  'requests~=2.7'
]

class PostDevelopCommand(develop):
  def run(self):
    make_director_executable()

class PostInstallCommand(install):
  def run(self):
    make_director_executable()

_DIRECTOR_DIR = os.path.join(os.path.dirname(__file__), 'eclipsegen', 'director')

def make_director_executable():
  print("Making director executable")
  os.chmod(os.path.join(_DIRECTOR_DIR, 'director'), 0o744)
  os.chmod(os.path.join(_DIRECTOR_DIR, 'director.bat'), 0o744)

setup(
  name='eclipsegen',
  version='0.4.2',
  description='Generate Eclipse instances in Python',
  url='http://github.com/Gohla/eclipsegen',
  author='Gabriel Konat',
  author_email='gabrielkonat@gmail.com',
  license='Apache 2.0',
  packages=['eclipsegen'],
  install_requires=dependencies,
  test_suite='nose.collector',
  tests_require=['nose>=1.3.7'] + dependencies,
  include_package_data=True,
  zip_safe=False,
  cmdclass={
    'install': PostInstallCommand,
    'develop': PostDevelopCommand
  }
)
