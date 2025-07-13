# compose_diff

`compose_diff` is a tool for creating change-sets of packages between two specified
Fedora Rawhide composes. It provides list of Rawhide composes available
at [recent Fedora Rawhide compose index](https://kojipkgs.fedoraproject.org/compose/rawhide/)
and computes package change-set diff between selected compose build versions.

## Installation

### Install as Python package

1. Clone this repo
2. Run `pip install .` in cloned repo root directory. This will install tool package.
3. Now you can invoke `compose_diff` from any directory provided your Python package
paths are setup properly.

### One-time use

1. Clone this repo
2. Install dependencies in the Python environment (system Python / virtualenv / pyenv / etc.)
in which you intend to use this tool by running `pip install -r requirements.txt`
from repo root directory.
3. Now you can start the tool by running `python3 compose_diff` from repo root directory.

## Usage

### Getting help

Use CLI option `-h` or `--help` to get help for any supported action.

Top level help:

```shell
$ compose_diff -h
usage: compose_diff [-h] [-v] {list,compare} ...

Fedora Rawhide compose differ

options:
  -h, --help      show this help message and exit
  -v, --version   show program's version number and exit

actions:
  {list,compare}
    list          List available compose versions
    compare       Compare compose versions
```

`list` action help:

```shell
$ compose_diff list -h
usage: compose_diff list [-h]

List available compose versions at https://kojipkgs.fedoraproject.org/compose/rawhide/

options:
  -h, --help  show this help message and exit
```

`compare` action help:

```shell
$ compose_diff compare -h
usage: compose_diff compare [-h] [-a {aarch64, x86_64}] [-j] VERSION-FROM [VERSION-TO]

Compare compose versions between VERSION-FROM and VERSION-TO. If VERSION-TO is not specified, the default value "latest" will be used instead.

positional arguments:
  VERSION

options:
  -h, --help            show this help message and exit
  -a {aarch64, x86_64}, --arch {aarch64, x86_64}
                        requested CPU architecture (default: x86_64)
  -j, --json-output
```

### Obtaining compose list

Run `compose_diff list` to obtain current list of Fedora Rawhide compose builds.

Example `list` output:

```shell
$ compose_diff list
Available Rawhide composes:
    20250629.n.0
    20250704.n.0
    20250704.n.1
    20250705.n.0
    20250706.n.0
    20250707.n.0
    20250708.n.0
    20250709.n.0
    20250710.n.0
    20250711.n.0
    20250712.n.0
    20250713.n.0
    latest
```

### Obtaining compose version diff

Run `compose_diff compare <VERSION-FROM> <VERSION-TO>` to get list of packages
removed, added or changed between to specified compose versions. If "\<VERSION-TO\>"
is not specified, default value "latest" will be used instead.

Example `compare` output (shortened for brevity):

```shell
$ compose_diff compare 20250711.n.0 20250712.n.0
======= x86_64 package diff from 20250711.n.0 to 20250712.n.0 =======
==== Packages REMOVED
     gtk-unico-engine REMOVED  (0:1.0.3-0.27.20140109bzr152)
     python-iso-639 REMOVED  (0:0.4.5-30)
     x-tile REMOVED  (0:3.3-17)
==== Packages ADDED
     python-packbits ADDED  (0:0.6-1)
     python-pyrankvote ADDED  (0:2.0.6-1)
     wayback ADDED  (0:0~git20250711.1.8bc189f-1)
==== Packages CHANGED
     PyGreSQL CHANGED  (0:6.0.1-7 -> 0:6.1.0-1)
     R-qpdf CHANGED  (0:1.4.0-1 -> 0:1.4.1-1)
     Singular CHANGED  (0:4.4.1-2 -> 0:4.4.1-5)
     ant CHANGED  (0:1.10.15-25 -> 0:1.10.15-27)
     apache-commons-exec CHANGED  (0:1.4.0-1 -> 0:1.5.0-1)
     argyllcms CHANGED  (0:3.3.0-2 -> 0:3.4.0-1)
     asahi-installer CHANGED  (0:0.7.8-5 -> 0:0.7.9-1)
     beets CHANGED  (0:2.3.1-1 -> 0:2.3.1-2)
     cbmc CHANGED  (0:6.7.0-1 -> 0:6.7.1-1)
     ccluster CHANGED  (0:1.1.7-9 -> 0:1.1.7-10)
     ...
```

#### Selecting diffed package CPU architecture

Please note that by default the diff is created by parsing **x86_64** CPU architecture
packages. If **aarch64** architecture packages should be diffed instead, use
`-a aarch64` or `--arch aarch64` CLI option like this:

```shell
compose_diff compare --arch aarch64 <VERSION-FROM> <VERSION-TO>
```

#### diff in machine readable (JSON) format

It is also possible to get tool output in JSON format jsut by including `-j` or
`--json-output` CLI option:

```shell
compose_diff compare --json-output <VERSION-FROM> <VERSION-TO>
```

Example of JSON output (shortened):

```shell
➜ python compose_diff compare --json-output 20250711.n.0 20250712.n.0
{
    "removed": [
        {
            "name": "gtk-unico-engine",
            "version": "0:1.0.3-0.27.20140109bzr152"
        },
        {
            "name": "python-iso-639",
            "version": "0:0.4.5-30"
        },
        {
            "name": "x-tile",
            "version": "0:3.3-17"
        }
    ],
    "added": [
        {
            "name": "python-packbits",
            "version": "0:0.6-1"
        },
        {
            "name": "python-pyrankvote",
            "version": "0:2.0.6-1"
        },
        {
            "name": "wayback",
            "version": "0:0~git20250711.1.8bc189f-1"
        }
    ],
    "changed": [
        {
            "name": "PyGreSQL",
            "version_from": "0:6.0.1-7",
            "version_to": "0:6.1.0-1"
        },
        {
            "name": "R-qpdf",
            "version_from": "0:1.4.0-1",
            "version_to": "0:1.4.1-1"
        },
        {
            "name": "Singular",
            "version_from": "0:4.4.1-2",
            "version_to": "0:4.4.1-5"
        },
        {
            "name": "ant",
            "version_from": "0:1.10.15-25",
            "version_to": "0:1.10.15-27"
        },
        ...
```
