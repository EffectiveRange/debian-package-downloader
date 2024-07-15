# debian-package-downloader

Debian package downloader that supports downloading packages from  .deb file URL and .deb GitHub release asset

## Table of Contents

- [Features](#features)
- [Requirements](#requirements)
- [Installation](#installation)
  - [Install from source root directory](#install-from-source-root-directory)
  - [Install from source distribution](#install-from-source-distribution)
- [Usage](#usage)
  - [Command line reference:](#command-line-reference)
  - [Example:](#example)

## Features

- [x] Download .deb files from file URL
- [x] Download .deb files from GitHub release asset
- [x] Can be used as a standalone library

## Requirements

- [Python3](https://www.python.org/downloads/)
- [PyGithub](https://pygithub.readthedocs.io/en/latest/index.html)
- [requests](https://requests.readthedocs.io/en/latest/)
- [pydantic](https://docs.pydantic.dev/latest/#pydantic-examples)

## Installation

### Install from source root directory

```bash
pip install .
```

### Install from source distribution

1. Create source distribution
    ```bash
    python setup.py sdist
    ```

2. Install from distribution file
    ```bash
    pip install dist/debian-package-downloader-1.0.0.tar.gz
    ```

3. Install from GitHub repository
    ```bash
    pip install git+https://github.com/EffectiveRange/debian-package-downloader.git@latest
    ```

## Usage

### Command line reference

```commandline
$ bin/debian-package-downloader.py --help
usage: debian-package-downloader.py [-h] [-f LOG_FILE] [-l LOG_LEVEL] [-d DOWNLOAD] package_config

positional arguments:
  package_config        package config JSON file path or URL

options:
  -h, --help            show this help message and exit
  -f LOG_FILE, --log-file LOG_FILE
                        log file path (default: None)
  -l LOG_LEVEL, --log-level LOG_LEVEL
                        logging level (default: info)
  -d DOWNLOAD, --download DOWNLOAD
                        package download location (default: /tmp/packages)
```

### Example

```commandline
$ bin/debian-package-downloader.py ~/config/package-config.json
```

Example configuration (example `package-config.json` config file content):

```json
[
  {
    "name": "wifi-manager",
    "release": {
      "repo": "EffectiveRange/wifi-manager",
      "tag": "latest",
      "matcher": "*armhf.deb"
    }
  },
  {
    "name": "pic18-q20-programmer",
    "release": {
      "repo": "EffectiveRange/pic18-q20-programmer",
      "tag": "v0.3.0",
      "matcher": "*armhf.deb"
    }
  },
  {
    "name": "filebeat",
    "file_url": "https://github.com/EffectiveRange/elastic-beats-armhf-deb/releases/download/v8.12.2/filebeat-8.12.2-armv7l.deb"
  }
]
```

Output:

```commandline
2024-07-04T07:06:18.199391Z [info     ] Starting package downloader    [PackageDownloaderApp] app_version=1.0.0 application=debian-package-downloader arguments={'log_file': None, 'log_level': 'info', 'download': '/tmp/packages', 'package_config': 'build/package-config.json'} hostname=Legion7iPro
2024-07-04T07:06:18.199758Z [info     ] Local file path provided, skipping download [FileDownloader] app_version=1.0.0 application=debian-package-downloader file=/home/attilagombos/EffectiveRange/debian-package-downloader/build/package-config.json hostname=Legion7iPro
2024-07-04T07:06:18.200043Z [info     ] Downloading packages           [PackageDownloader] app_version=1.0.0 application=debian-package-downloader hostname=Legion7iPro packages=['wifi-manager', 'pic18-q20-programmer', 'filebeat']
2024-07-04T07:06:18.200251Z [info     ] Downloading package file from release [DebDownloader] app_version=1.0.0 application=debian-package-downloader hostname=Legion7iPro package=wifi-manager release=ReleaseConfig(EffectiveRange/wifi-manager.git@latest, matcher=*armhf.deb, has_token=False)
2024-07-04T07:06:18.894080Z [info     ] Found release for tag          [DebDownloader] app_version=1.0.0 application=debian-package-downloader hostname=Legion7iPro repo=wifi-manager tag=latest
2024-07-04T07:06:19.300348Z [info     ] Found matching asset           [AssetDownloader] app_version=1.0.0 application=debian-package-downloader asset=wifi-manager_1.0.5_armhf.deb hostname=Legion7iPro release=ReleaseConfig(EffectiveRange/wifi-manager.git@latest, matcher=*armhf.deb, has_token=False)
2024-07-04T07:06:19.300732Z [info     ] Downloading file               [FileDownloader] app_version=1.0.0 application=debian-package-downloader file_name=wifi-manager_1.0.5_armhf.deb headers=['Accept'] hostname=Legion7iPro url=https://api.github.com/repos/EffectiveRange/wifi-manager/releases/assets/175922814
2024-07-04T07:06:20.137266Z [info     ] Downloaded file                [FileDownloader] app_version=1.0.0 application=debian-package-downloader file=/tmp/packages/wifi-manager_1.0.5_armhf.deb hostname=Legion7iPro
2024-07-04T07:06:20.137859Z [info     ] Downloading package file from release [DebDownloader] app_version=1.0.0 application=debian-package-downloader hostname=Legion7iPro package=pic18-q20-programmer release=ReleaseConfig(EffectiveRange/pic18-q20-programmer.git@v0.3.0, matcher=*armhf.deb, has_token=False)
2024-07-04T07:06:20.802212Z [info     ] Found release for tag          [DebDownloader] app_version=1.0.0 application=debian-package-downloader hostname=Legion7iPro repo=pic18-q20-programmer tag=v0.3.0
2024-07-04T07:06:21.219820Z [info     ] Found matching asset           [AssetDownloader] app_version=1.0.0 application=debian-package-downloader asset=picprogrammer_0.3.0-1_armhf.deb hostname=Legion7iPro release=ReleaseConfig(EffectiveRange/pic18-q20-programmer.git@v0.3.0, matcher=*armhf.deb, has_token=False)
2024-07-04T07:06:21.220929Z [info     ] Downloading file               [FileDownloader] app_version=1.0.0 application=debian-package-downloader file_name=picprogrammer_0.3.0-1_armhf.deb headers=['Accept'] hostname=Legion7iPro url=https://api.github.com/repos/EffectiveRange/pic18-q20-programmer/releases/assets/175069584
2024-07-04T07:06:22.041703Z [info     ] Downloaded file                [FileDownloader] app_version=1.0.0 application=debian-package-downloader file=/tmp/packages/picprogrammer_0.3.0-1_armhf.deb hostname=Legion7iPro
2024-07-04T07:06:22.042276Z [info     ] Downloading package file from file URL [DebDownloader] app_version=1.0.0 application=debian-package-downloader hostname=Legion7iPro package=filebeat url=https://github.com/EffectiveRange/elastic-beats-armhf-deb/releases/download/v8.12.2/filebeat-8.12.2-armv7l.deb
2024-07-04T07:06:22.042593Z [info     ] Downloading file               [FileDownloader] app_version=1.0.0 application=debian-package-downloader file_name=None headers=[] hostname=Legion7iPro url=https://github.com/EffectiveRange/elastic-beats-armhf-deb/releases/download/v8.12.2/filebeat-8.12.2-armv7l.deb
2024-07-04T07:06:22.950503Z [info     ] Downloaded file                [FileDownloader] app_version=1.0.0 application=debian-package-downloader file=/tmp/packages/filebeat-8.12.2-armv7l.deb hostname=Legion7iPro
```
