import os
import shutil
from unittest import TestCase

from eclipsegen.generate import EclipseGenerator, EclipseMultiGenerator, Os, Arch
from eclipsegen.preset import Presets, Preset

_DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')


class TestPreset(Preset):
  @property
  def repositories(self):
    return ['http://ftp.snt.utwente.nl/pub/software/eclipse/eclipse/updates/4.6/']

  @property
  def install_units(self):
    return ['org.eclipse.platform.ide']


class Test(TestCase):
  @classmethod
  def setUpClass(cls):
    # Ensure the data directory exists
    if not os.path.exists(_DATA_DIR):
      os.makedirs(_DATA_DIR)

  def test_eclipse_generate_noop(self):
    repositories, installUnits = Presets.combine_presets([TestPreset()])
    generator = EclipseGenerator(workingDir=_DATA_DIR, destination='noop', repositories=repositories,
      installUnits=[], name='eclipse-test-noop', fixIni=False)
    generator.generate()

  def test_longrunning_eclipse_generate(self):
    destination = 'eclipse-single'
    shutil.rmtree(os.path.join(_DATA_DIR, destination), ignore_errors=True)

    repositories, installUnits = Presets.combine_presets([TestPreset()])
    generator = EclipseGenerator(workingDir=_DATA_DIR, destination=destination, repositories=repositories,
      installUnits=installUnits, name='eclipse-test-single')
    generator.generate()

  def test_longrunning_eclipse_multi_gen(self):
    destination = 'eclipse-multiple'
    shutil.rmtree(os.path.join(_DATA_DIR, destination), ignore_errors=True)

    repositories, installUnits = Presets.combine_presets([TestPreset()])
    generator = EclipseMultiGenerator(workingDir=_DATA_DIR, destination=destination,
      oss=[Os.windows.value, Os.macosx.value, Os.linux.value], archs=[Arch.x64.value], repositories=repositories,
      installUnits=installUnits, name='eclipse-test-multiple', addJre=True, archiveJreSeparately=True,
      archivePrefix='eclipse-test-multiple', archiveSuffix='-test-suffix')
    generator.generate()
