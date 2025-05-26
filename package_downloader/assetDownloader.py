# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import fnmatch
from collections import OrderedDict
from typing import Optional

from common_utility import IFileDownloader
from context_logger import get_logger
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset

from package_downloader import ReleaseConfig

log = get_logger('AssetDownloader')


class IAssetDownloader(object):

    def download(self, config: ReleaseConfig, release: GitRelease, first_match_only: bool = False,
                 skip_if_exists: bool = True) -> list[str]:
        raise NotImplementedError()


class AssetDownloader(IAssetDownloader):

    def __init__(self, file_downloader: IFileDownloader, distro_map: Optional[OrderedDict[str, str]] = None,
                 private_dir: str = 'private') -> None:
        self._file_downloader = file_downloader
        self._distro_map = distro_map if distro_map else {}
        self._private_dir = private_dir

    def download(self, config: ReleaseConfig, release: GitRelease, first_match_only: bool = False,
                 skip_if_exists: bool = True) -> list[str]:
        assets = release.get_assets()

        log.debug('Retrieved asset list', release=config, assets=[asset.name for asset in assets])

        downloaded_files = []

        for asset in assets:
            if fnmatch.fnmatch(asset.name, config.matcher):
                log.info('Found matching asset', release=config, asset=asset.name)

                headers = {'Accept': 'application/octet-stream'}

                if config.raw_token:
                    headers['Authorization'] = f'token {config.raw_token}'

                if self._distro_map:
                    downloaded_files.extend(self._download_for_distro(asset, headers, config.private))
                else:
                    sub_dir = self._private_dir if config.private else None
                    downloaded_files.append(self._file_downloader.download(asset.url, asset.name, sub_dir, headers))

                if first_match_only:
                    break

        if not downloaded_files:
            log.error('No matching asset found', release=config, assets=[asset.name for asset in assets])
            raise ValueError('No matching asset found')

        return downloaded_files

    def _download_for_distro(self, asset: GitReleaseAsset, headers: dict[str, str], private: bool) -> list[str]:
        for distro_matcher, distro_dir in self._distro_map.items():
            if distro_matcher in asset.name:
                sub_dir = self._get_sub_dir(distro_dir, private)
                return [self._file_downloader.download(asset.url, asset.name, sub_dir, headers)]

        sub_dirs = [self._get_sub_dir(distro_dir, private) for distro_dir in self._distro_map.values()]
        return self._file_downloader.download_and_copy(asset.url, sub_dirs, asset.name, headers)

    def _get_sub_dir(self, sub_dir: str, private: bool) -> str:
        return f'{sub_dir}/{self._private_dir}' if private else sub_dir
