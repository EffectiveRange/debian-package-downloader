# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import fnmatch
from typing import Optional

from common_utility import IFileDownloader
from context_logger import get_logger
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset

from package_downloader import ReleaseConfig

log = get_logger('AssetDownloader')


class IAssetDownloader(object):

    def download(
        self, config: ReleaseConfig, release: GitRelease, first_match_only: bool = False, skip_if_exists: bool = True
    ) -> list[str]:
        raise NotImplementedError()


class AssetDownloader(IAssetDownloader):

    def __init__(self, file_downloader: IFileDownloader) -> None:
        self._file_downloader = file_downloader

    def download(
        self, config: ReleaseConfig, release: GitRelease, first_match_only: bool = False, skip_if_exists: bool = True
    ) -> list[str]:
        assets = release.get_assets()

        log.debug('Retrieved asset list', release=config, assets=[asset.name for asset in assets])

        downloaded_files = []

        for asset in assets:
            if fnmatch.fnmatch(asset.name, config.matcher):
                log.info('Found matching asset', release=config, asset=asset.name)

                downloaded_files.append(self._download_asset(asset, config.raw_token))

                if first_match_only:
                    break

        if not downloaded_files:
            log.error('No matching asset found', release=config, assets=[asset.name for asset in assets])
            raise ValueError('No matching asset found')

        return downloaded_files

    def _download_asset(self, asset: GitReleaseAsset, token: Optional[str] = None) -> str:
        log.debug('Downloading asset', asset=asset.name)

        headers = {'Accept': 'application/octet-stream'}

        if token:
            headers['Authorization'] = f'token {token}'

        return self._file_downloader.download(asset.url, asset.name, headers)
