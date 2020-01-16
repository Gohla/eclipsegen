from setuptools import setup

dependencies = [
  'requests~=2.7'
]

setup(
  name='eclipsegen',
  version='0.4.1',
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
)
