# eclipsegen
Generate Eclipse instances using Python.

This project requires:
- Python 3.10 and newer
- Java 11 and newer

## Build & Test
If you have a local installation of Eclipse, set the `$ECLIPSE_HOME` environment variable to point to the directory
that contains the `eclipse` or `eclipse.exe` executable.

```shell
export ECLIPSE_HOME=~/eclipse/
```

Alternatively, you can provide the URL to a mirror where an appropriate version of Eclipse can be downloaded from.
Usually you would pick the Linux version of the Platform Runtime Binary, say from [this page](https://archive.eclipse.org/eclipse/downloads/drops4/R-4.21-202109060500/). If you specify nothing, Eclipse is downloaded from this URL by default:

```shell
export ECLIPSE_URL=https://artifacts.metaborg.org/content/repositories/releases/org/eclipse/eclipse-platform/4.21/eclipse-platform-4.21-linux-gtk-x86_64.tar.gz
```

Finally, enable the appropriate Java version (e.g., `sdk use java 17.0.8-tem`), then create a virtual environment and run the tests:

```shell
virtualenv venv
source venv/bin/activate
pip install -e .[test]      # Install in editable mode with test dependencies
python -m pytest            # Run the tests
```

## License
Copyright 2016-2023 Gabriel Konat

Licensed under the Apache License, Version 2.0 (the "License"); you may not use this file except in compliance with the License. You may obtain a copy of the License at <http://www.apache.org/licenses/LICENSE-2.0>.

Unless required by applicable law or agreed to in writing, software distributed under the License is distributed on an **"as is" basis, without warranties or conditions of any kind**, either express or implied. See the License for the specific language governing permissions and limitations under the License.
