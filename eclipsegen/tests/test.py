import os
import shutil
from unittest import TestCase

from eclipsegen.generate import EclipseGenerator, EclipseMultiGenerator, Os, Arch
from eclipsegen.preset import Presets

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class Test(TestCase):
  def test_eclipse_gen(self):
    destination = 'eclipse-single'
    shutil.rmtree(os.path.join(_DATA_DIR, destination), ignore_errors=True)

    repositories, installUnits = Presets.combine_presets([Presets.platform.value])
    generator = EclipseGenerator(workingDir=_DATA_DIR, destination=destination, repositories=repositories,
      installUnits=installUnits, name='eclipse-test-single')
    generator.generate()

  def test_eclipse_multi_gen(self):
    destination = 'eclipse-multiple'
    shutil.rmtree(os.path.join(_DATA_DIR, destination), ignore_errors=True)

    repositories, installUnits = Presets.combine_presets([Presets.platform.value])
    generator = EclipseMultiGenerator(workingDir=_DATA_DIR, destination=destination,
      oss=[Os.windows.value, Os.macosx.value, Os.linux.value], archs=[Arch.x64.value], repositories=repositories,
      installUnits=installUnits, name='eclipse-test-multiple', addJre=True, archiveJreSeparately=True,
      archivePrefix='eclipse-test-multiple', archiveSuffix='-test-suffix')
    generator.generate()
