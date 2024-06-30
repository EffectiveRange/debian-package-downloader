#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace
from pathlib import Path

from context_logger import get_logger, setup_logging

from package_downloader import FileDownloader, DebDownloader, RepositoryProvider, \
    SessionProvider, AssetDownloader, PackageDownloader, JsonLoader

log = get_logger('PackageDownloaderApp')


def main() -> None:
    arguments = _get_arguments()

    setup_logging('debian-package-downloader', arguments.log_level, arguments.log_file)

    log.info('Starting package downloader', arguments=vars(arguments))

    json_loader = JsonLoader()

    session_provider = SessionProvider()
    repository_provider = RepositoryProvider()
    file_downloader = FileDownloader(session_provider, _get_absolute_path(arguments.download))
    asset_downloader = AssetDownloader(file_downloader)
    deb_downloader = DebDownloader(repository_provider, asset_downloader, file_downloader)

    package_downloader = PackageDownloader(_get_absolute_path(arguments.package_config), json_loader, deb_downloader)

    package_downloader.download_packages()


def _get_arguments() -> Namespace:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--log-file', help='log file path')
    parser.add_argument('-l', '--log-level', help='logging level', default='info')
    parser.add_argument('-d', '--download', help='package download location', default='/tmp/packages')

    parser.add_argument('package_config', help='package config JSON file')

    return parser.parse_args()


def _get_absolute_path(path: str) -> str:
    return path if path.startswith('/') else f'{_get_resource_root()}/{path}'


def _get_resource_root() -> str:
    return str(Path(os.path.dirname(__file__)).parent.absolute())


if __name__ == '__main__':
    main()
