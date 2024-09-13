#!/usr/bin/env python3

# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import os
from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter, Namespace

from common_utility import SessionProvider, FileDownloader
from common_utility.jsonLoader import JsonLoader
from context_logger import get_logger, setup_logging

from package_downloader import DebDownloader, RepositoryProvider, AssetDownloader, PackageDownloader

log = get_logger('PackageDownloaderApp')


def main() -> None:
    arguments = _get_arguments()

    setup_logging('debian-package-downloader', arguments.log_level, arguments.log_file)

    log.info('Starting package downloader', arguments=vars(arguments))

    json_loader = JsonLoader()

    session_provider = SessionProvider()
    repository_provider = RepositoryProvider()
    file_downloader = FileDownloader(session_provider, os.path.abspath(arguments.download))
    asset_downloader = AssetDownloader(file_downloader)
    deb_downloader = DebDownloader(repository_provider, asset_downloader, file_downloader)

    package_config_path = file_downloader.download(arguments.package_config, skip_if_exists=False)

    package_downloader = PackageDownloader(package_config_path, json_loader, deb_downloader)

    package_downloader.download_packages()


def _get_arguments() -> Namespace:
    parser = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)
    parser.add_argument('-f', '--log-file', help='log file path')
    parser.add_argument('-l', '--log-level', help='logging level', default='info')
    parser.add_argument('-d', '--download', help='package download location', default='/tmp/packages')

    parser.add_argument('package_config', help='package config JSON file path or URL')

    return parser.parse_args()


if __name__ == '__main__':
    main()
