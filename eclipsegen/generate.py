import tarfile
import tempfile
import urllib.parse
import urllib.request
from enum import Enum, unique
from itertools import takewhile
from os import path, makedirs, listdir, rmdir, mkdir, remove, walk, chmod
from platform import architecture, system
from re import sub, findall, MULTILINE
from shutil import move, copytree, rmtree, make_archive
from stat import S_IWRITE
from subprocess import Popen
from sys import maxsize

import requests

from eclipsegen.config import X86Arch, X64Arch, WindowsOs, MacOs, LinuxOs


@unique
class Os(Enum):
  windows = WindowsOs()
  macOs = MacOs()
  linux = LinuxOs()

  @staticmethod
  def get_current():
    sys = system()
    if sys == 'Windows':
      return Os.windows.value
    elif sys == 'Darwin':
      return Os.macOs.value
    elif sys == 'Linux':
      return Os.linux.value
    else:
      raise Exception('Unsupported OS {}'.format(sys))


@unique
class Arch(Enum):
  x64 = X64Arch()
  x86 = X86Arch()

  @staticmethod
  def get_current():
    if architecture()[0] == '64bit':
      return Arch.x64.value
    if maxsize > 2 ** 32:
      return Arch.x64.value
    return Arch.x86.value


__invalidCombinations = [
  (Os.macOs.value, Arch.x86.value, True),
  # (Os.macOs.value, Arch.x86.value, False)
]


def _is_invalid_combination(os, arch, addJre):
  for incorrectOs, incorrectArch, incorrectAddJre in __invalidCombinations:
    if os == incorrectOs and arch == incorrectArch and incorrectAddJre == addJre:
      return True
  return False


class EclipseMultiGenerator(object):
  def __init__(self, workingDir, destination, oss=None, archs=None, addJres=None, repositories=None, installUnits=None):
    self.workingDir = workingDir
    self.destination = destination
    self.oss = oss if oss else [o.value for o in Os]
    self.archs = archs if archs else [a.value for a in Arch]
    self.addJres = addJres if addJres else [True, False]
    self.repositories = repositories
    self.installUnits = installUnits

  def generate_all(self):
    combinations = [(o, a, j) for o in self.oss for a in self.archs for j in self.addJres]
    print('Generating an Eclipse instance for following feature combinations:')
    for os, arch, addJre in combinations:
      if not _is_invalid_combination(os, arch, addJre):
        print('  {}, {}, {}'.format(os.name, arch.name, 'include JRE' if addJre else 'no JRE'))
    for os, arch, addJre in combinations:
      if not _is_invalid_combination(os, arch, addJre):
        print('Generating Eclipse for combination {}, {}, {}'.format(os.name, arch.name,
          'include JRE' if addJre else 'no JRE'))
        generator = EclipseGenerator(self.workingDir, self.destination, os=os, arch=arch,
          repositories=self.repositories, installUnits=self.installUnits, fixIni=True, addJre=addJre, archive=True)
        generator.generate()


class EclipseGenerator(object):
  def __init__(self, workingDir, destination, os=None, arch=None, repositories=None, installUnits=None,
      fixIni=True, addJre=False, archive=False, archivePrefix='eclipse', archivePostfix=''):
    self.os = os if os else Os.get_current()
    self.arch = arch if arch else Arch.get_current()
    self.repositories = repositories if repositories else []
    self.installUnits = installUnits if installUnits else []

    self.workingDir = workingDir
    if not path.isabs(self.workingDir):
      self.workingDir = path.abspath(self.workingDir)

    self.requestedDestination = _make_abs(destination, self.workingDir)

    if archive:
      self.tempdir = tempfile.TemporaryDirectory()
      self.destination = self.tempdir.name
    else:
      self.destination = self.requestedDestination

    self.finalDestination = self.os.finalDestination(self.destination, 'Eclipse.app')

    self.fixIni = fixIni
    self.addJre = addJre
    self.archive = archive
    self.archivePrefix = archivePrefix
    self.archivePostfix = archivePostfix

  def __enter__(self):
    return self

  def __exit__(self, **_):
    if self.archive:
      print('Deleting temporary directory {}'.format(self.tempdir))
      self.tempdir.cleanup()

  def generate(self):
    if _is_invalid_combination(self.os, self.arch, self.addJre):
      raise RuntimeError(
        'Combination {}, {}, {} is invalid, cannot generate Eclipse instance'.format(self.os, self.arch, self.addJre))
    directorBin = 'director.bat' if self.os == Os.windows.value else 'director'
    director = path.join(path.dirname(path.realpath(__file__)), 'director', directorBin)
    args = [director]

    if len(self.repositories) != 0:
      mappedRepositories = map(self.__to_uri, self.repositories)
      args.extend(['-r {}'.format(repo) for repo in mappedRepositories])

    args.extend(['-i {}'.format(iu) for iu in self.installUnits])

    args.append('-tag InitialState')
    args.append('-destination {}'.format(self.finalDestination))
    args.append('-profile SDKProfile')
    args.append('-profileProperties "org.eclipse.update.install.features=true"')
    args.append('-p2.os {}'.format(self.os.eclipseOs))
    args.append('-p2.ws {}'.format(self.os.eclipseWs))
    args.append('-p2.arch {}'.format(self.arch.eclipseArch))
    args.append('-roaming')

    cmd = ' '.join(args)
    print(cmd)
    try:
      process = Popen(cmd, cwd=self.workingDir, shell=True)
      process.communicate()
      if process.returncode != 0:
        raise RuntimeError("Eclipse generation failed")
    except KeyboardInterrupt:
      raise RuntimeError("Eclipse generation interrupted")

    if self.fixIni:
      self.fix_ini()
    if self.addJre:
      self.add_jre()
    # Make everything writeable such that it can be deleted from temp dirs.
    _make_writeable(self.finalDestination)
    if self.archive:
      self.create_archive(prefix=self.archivePrefix, postfix=self.archivePostfix)

  def fix_ini(self, stackSize='16M', heapSize='1G', maxHeapSize='1G', maxPermGen='256M',
      requiredJavaVersion='1.8', server=True):
    iniLocation = self.os.iniLocation(self.finalDestination)

    # Python converts all line endings to '\n' when reading a file in text mode like this.
    with open(iniLocation, "r") as iniFile:
      iniText = iniFile.read()

    iniText = sub(r'--launcher\.XXMaxPermSize\n[0-9]+[gGmMkK]', '', iniText, flags=MULTILINE)
    iniText = sub(r'-install\n.+', '', iniText, flags=MULTILINE)
    iniText = sub(r'-showsplash\norg.eclipse.platform', '', iniText, flags=MULTILINE)

    launcherPattern = r'--launcher\.defaultAction\nopenFile'
    launcherMatches = len(findall(launcherPattern, iniText, flags=MULTILINE))
    if launcherMatches > 1:
      iniText = sub(launcherPattern, '', iniText, count=launcherMatches - 1, flags=MULTILINE)

    iniText = sub(r'-X(ms|ss|mx)[0-9]+[gGmMkK]', '', iniText)
    iniText = sub(r'-XX:MaxPermSize=[0-9]+[gGmMkK]', '', iniText)
    iniText = sub(r'-Dorg\.eclipse\.swt\.internal\.carbon\.smallFonts', '', iniText)
    iniText = sub(r'-XstartOnFirstThread', '', iniText)
    iniText = sub(r'-Dosgi.requiredJavaVersion=[0-9]\.[0-9]', '', iniText)
    iniText = sub(r'-server', '', iniText)

    iniText = '\n'.join([line for line in iniText.split('\n') if line.strip()]) + '\n'

    if self.os == Os.macOs.value:
      iniText += '-XstartOnFirstThread\n'

    if stackSize:
      iniText += '-Xss{}\n'.format(stackSize)
    if heapSize:
      iniText += '-Xms{}\n'.format(heapSize)
    if maxHeapSize:
      iniText += '-Xmx{}\n'.format(maxHeapSize)
    if maxPermGen:
      iniText += '-XX:MaxPermSize={}\n'.format(maxPermGen)

    if requiredJavaVersion:
      iniText += '-Dosgi.requiredJavaVersion={}\n'.format(requiredJavaVersion)

    if server:
      iniText += '-server\n'

    print('Setting contents of {} to:\n{}'.format(iniLocation, iniText))
    with open(iniLocation, "w") as iniFile:
      iniFile.write(iniText)

  def add_jre(self):
    jrePath = self.__download_jre()
    targetJrePath = path.join(self.finalDestination, 'jre')
    if path.isdir(targetJrePath):
      rmtree(targetJrePath, ignore_errors=True)
    print('Copying JRE from {} to {}'.format(jrePath, targetJrePath))
    copytree(jrePath, targetJrePath, symlinks=True)

    relJreLocation = self.os.jreLocation(self.arch == Arch.x64.value)
    iniLocation = self.os.iniLocation(self.finalDestination)
    with open(iniLocation, 'r') as iniFile:
      iniText = iniFile.read()
    with open(iniLocation, 'w') as iniFile:
      print('Prepending VM location {} to eclipse.ini'.format(relJreLocation))
      iniText = sub(r'-vm\n.+\n', '', iniText, flags=MULTILINE)
      iniFile.write('-vm\n{}\n'.format(relJreLocation) + iniText)

  def create_archive(self, prefix='eclipse', postfix=''):
    name = '{}-{}-{}{}{}'.format(prefix, self.os.name, self.arch.name, '-jre' if self.addJre else '', postfix)
    print('Archiving Eclipse instance {}'.format(name))
    filename = path.join(self.requestedDestination, name)
    with tempfile.TemporaryDirectory() as tempdir:
      # Copy into another temp dir to have a directory with name as the root in archive, instead of the Eclipse directory.
      copytree(self.destination, path.join(tempdir, name), symlinks=True)
      return make_archive(filename, format=self.os.archiveFormat, root_dir=tempdir, base_dir=name)

  def __to_uri(self, location):
    if location.startswith('http'):
      return location
    else:
      location = _make_abs(location, self.workingDir)
      return urllib.parse.urljoin('file:', urllib.request.pathname2url(location))

  def __download_jre(self):
    version = '8u92'
    build = 'b14'
    urlPrefix = 'http://download.oracle.com/otn-pub/java/jdk/{0}-{1}/jre-{0}-'.format(version, build)
    extension = 'tar.gz'
    jreOs = self.os.jreOs
    jreArch = self.arch.jreArch

    location = _to_storage_location(path.join('jre', version, build))
    makedirs(location, exist_ok=True)

    fileName = '{}-{}.{}'.format(jreOs, jreArch, extension)
    filePath = path.join(location, fileName)

    dirName = '{}-{}'.format(jreOs, jreArch)
    dirPath = path.join(location, dirName)

    if path.isdir(dirPath):
      return dirPath

    url = '{}{}'.format(urlPrefix, fileName)
    print('Downloading JRE from {}'.format(url))
    cookies = dict(gpw_e24='http%3A%2F%2Fwww.oracle.com%2F', oraclelicense='accept-securebackup-cookie')
    request = requests.get(url, cookies=cookies)
    with open(filePath, 'wb') as file:
      for chunk in request.iter_content(1024):
        file.write(chunk)

    print('Extracting JRE to {}'.format(dirPath))
    with tarfile.open(filePath, 'r') as tar:
      tar.extractall(path=dirPath)
      rootName = _common_prefix(tar.getnames())
      rootDir = path.join(dirPath, rootName)
      for name in listdir(rootDir):
        move(path.join(rootDir, name), path.join(dirPath, name))
      rmdir(rootDir)

    remove(filePath)

    return dirPath


def _to_storage_location(location):
  storageLocation = path.join(path.expanduser('~'), '.eclipsegen')
  if not path.isdir(storageLocation):
    mkdir(storageLocation)
  return path.join(storageLocation, location)


def _common_prefix(paths, sep='/'):
  """
  Finds the common path prefix in given list of paths.
  The os.path.commonprefix function is broken, since it finds prefixes on the character level, not the path level.
  From: http://rosettacode.org/wiki/Find_Common_Directory_Path#Python
  """
  byDirectoryLevels = zip(*[p.split(sep) for p in paths])

  def all_names_equal(name):
    return all(n == name[0] for n in name[1:])

  return sep.join(x[0] for x in takewhile(all_names_equal, byDirectoryLevels))


def _make_abs(directory, relativeTo):
  if not path.isabs(directory):
    return path.normpath(path.join(directory, relativeTo))
  return directory


def _make_writeable(directory):
  for root, _, files in walk(directory):
    for name in files:
      full_path = path.join(root, name)
      chmod(full_path, S_IWRITE)
