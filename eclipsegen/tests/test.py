import os
from unittest import TestCase

from eclipsegen.generate import EclipseGenerator, Os, Arch, EclipseMultiGenerator

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')

_repositories = ['http://eclipse.mirror.triple-it.nl/releases/neon/',
                 'http://eclipse.mirror.triple-it.nl/eclipse/updates/4.6']
_installUnits = ['epp.package.java', 'org.eclipse.platform.feature.group', 'org.eclipse.jdt.feature.group',
                 'org.eclipse.m2e.feature.feature.group', 'org.eclipse.jgit.feature.group']


class Test(TestCase):
  def test_eclipse_gen(self):
    generator = EclipseGenerator(_DATA_DIR, 'eclipse', os=Os.macOs.value, arch=Arch.x64.value, archive=True,
      repositories=_repositories, installUnits=_installUnits)
    # generator.generate()

  def test_eclipse_multi_gen(self):
    generator = EclipseMultiGenerator(_DATA_DIR, 'eclipse', repositories=_repositories, installUnits=_installUnits,
      name='spoofax', archivePrefix='spoofax')
    generator.generate_all()
