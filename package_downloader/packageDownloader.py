# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

from common_utility.jsonLoader import IJsonLoader
from context_logger import get_logger

from package_downloader import IDebDownloader, PackageConfig

log = get_logger('PackageDownloader')


class PackageDownloader(object):

    def __init__(self, config_path: str, json_loader: IJsonLoader, deb_downloader: IDebDownloader) -> None:
        self._config_path = config_path
        self._json_loader = json_loader
        self._deb_downloader = deb_downloader

    def download_packages(self) -> None:
        config_list = self._json_loader.load_list(self._config_path, PackageConfig)

        log.info('Downloading packages', packages=[config.package for config in config_list])

        for config in config_list:
            self._download_package(config)

    def _download_package(self, config: PackageConfig) -> None:
        try:
            log.debug('Downloading package', package=config.package)
            file_path = self._deb_downloader.download(config)
            log.debug('Downloaded package', package=config.package, file=file_path)
        except Exception as error:
            log.error('Failed to download package', package=config.package, error=error)
