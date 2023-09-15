from setuptools import setup
import os

dependencies = [
  'requests~=2.7'
]

setup(
  name='eclipsegen',
  version='0.5.0',
  description='Generate Eclipse instances in Python',
  url='http://github.com/Gohla/eclipsegen',
  author='Gabriel Konat',
  author_email='gabrielkonat@gmail.com',
  license='Apache 2.0',
  packages=['eclipsegen'],
  install_requires=dependencies,
  test_suite='eclipsegen.tests',
  tests_require=['pytest~=7.4.2'] + dependencies,
  include_package_data=True,
)
