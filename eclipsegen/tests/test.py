import os
from unittest import TestCase

from eclipsegen.generate import EclipseMultiGenerator

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class Test(TestCase):
  # def test_eclipse_gen(self):
  #   generator = EclipseGenerator(_DATA_DIR, 'eclipse', os=Os.windows.value, arch=Arch.x64.value,
  #     repositories=['http://eclipse.mirror.triple-it.nl/releases/neon/',
  #                   'http://eclipse.mirror.triple-it.nl/eclipse/updates/4.6'],
  #     installUnits=['epp.package.java', 'org.eclipse.platform.feature.group', 'org.eclipse.jdt.feature.group',
  #                   'org.eclipse.m2e.feature.feature.group', 'org.eclipse.jgit.feature.group'])
  #   generator.generate()

  def test_eclipse_multi_gen(self):
    generator = EclipseMultiGenerator(_DATA_DIR, 'eclipse',
      repositories=['http://eclipse.mirror.triple-it.nl/releases/neon/',
                    'http://eclipse.mirror.triple-it.nl/eclipse/updates/4.6'],
      installUnits=['epp.package.java', 'org.eclipse.platform.feature.group', 'org.eclipse.jdt.feature.group',
                    'org.eclipse.m2e.feature.feature.group', 'org.eclipse.jgit.feature.group'])
    generator.generate_all()
