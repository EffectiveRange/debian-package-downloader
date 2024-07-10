# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

from typing import Optional

from context_logger import get_logger
from github.GitRelease import GitRelease

from package_downloader import PackageConfig, IFileDownloader, IAssetDownloader, ReleaseConfig, IRepositoryProvider

log = get_logger('DebDownloader')


class IDebDownloader(object):

    def download(self, package: PackageConfig) -> Optional[str]:
        raise NotImplementedError()


class DebDownloader(IDebDownloader):

    def __init__(self, repository_provider: IRepositoryProvider, asset_downloader: IAssetDownloader,
                 file_downloader: IFileDownloader):
        self._repository_provider = repository_provider
        self._asset_downloader = asset_downloader
        self._file_downloader = file_downloader

    def download(self, config: PackageConfig) -> Optional[str]:
        package_file = None

        if config.file_url:
            log.info('Downloading package file from file URL', package=config.package, url=config.file_url)
            package_file = self._file_downloader.download(config.file_url)

        if not package_file and (release_config := config.release):
            log.info('Downloading package file from release', package=config.package, release=release_config)
            release = self._get_release(release_config)
            package_file = self._asset_downloader.download(release_config, release, first_match_only=True)[0]

        if not package_file:
            log.error('No download source configured', config=config)
            raise ValueError('No download source configured')

        return package_file

    def _get_release(self, release_config: ReleaseConfig) -> GitRelease:
        repository = self._repository_provider.get_repository(release_config)

        log.debug('Getting release from repository', repo=repository.name, tag=release_config.tag)

        release = repository.get_release(release_config.tag)

        if not release:
            log.error('Release not found for tag', repo=repository.name, tag=release_config.tag)
            raise ValueError('Release not found')

        log.info('Found release for tag', repo=repository.name, tag=release_config.tag)

        return release
