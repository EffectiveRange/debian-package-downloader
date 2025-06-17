# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import fnmatch
from collections import OrderedDict
from pathlib import Path
from typing import Optional, Union

from common_utility import IFileDownloader
from context_logger import get_logger
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset
from tenacity import retry, wait_fixed, stop_after_attempt

from package_downloader import ReleaseConfig

log = get_logger('AssetDownloader')


class IAssetDownloader(object):

    def download(self, config: ReleaseConfig, release: GitRelease, first_match_only: bool = False,
                 skip_if_exists: bool = True) -> list[Path]:
        raise NotImplementedError()


class AssetDownloader(IAssetDownloader):

    def __init__(self, file_downloader: IFileDownloader, distro_map: Optional[OrderedDict[str, str]] = None,
                 private_dir: Path = Path('private')) -> None:
        self._file_downloader = file_downloader
        self._distro_map = distro_map if distro_map else {}
        self._private_dir = private_dir

    def download(self, config: ReleaseConfig, release: GitRelease, first_match_only: bool = False,
                 skip_if_exists: bool = True) -> list[Path]:
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
                    downloaded_files.extend(self._download_for_distro(asset, headers, config.is_private))
                else:
                    downloaded_files.append(self._download(asset.url, asset.name, None, headers, config.is_private))

                if first_match_only:
                    break

        if not downloaded_files:
            log.error('No matching asset found', release=config, assets=[asset.name for asset in assets])
            raise ValueError('No matching asset found')

        return downloaded_files

    def _download_for_distro(self, asset: GitReleaseAsset, headers: dict[str, str], private: bool) -> list[Path]:
        for distro_matcher, distro_dir in self._distro_map.items():
            if distro_matcher in asset.name:
                return [self._download(asset.url, asset.name, Path(distro_dir), headers, private)]

        return self._download_and_copy(asset.url, asset.name, headers, private)

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
    def _download(self, url: str, filename: str, sub_dir: Optional[Path], headers: dict[str, str],
                  private: bool) -> Path:
        sub_dir = self._get_sub_dir(sub_dir, private) if sub_dir else (self._private_dir if private else None)
        return self._file_downloader.download(url, filename, sub_dir, headers)

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
    def _download_and_copy(self, url: str, filename: str, headers: dict[str, str], private: bool) -> list[Path]:
        sub_dirs: list[Union[str, Path]] = [
            self._get_sub_dir(Path(sub_dir), private) for sub_dir in self._distro_map.values()
        ]
        return self._file_downloader.download_and_copy(url, sub_dirs, filename, headers)

    def _get_sub_dir(self, sub_dir: Path, private: bool) -> Path:
        return sub_dir / self._private_dir if private else sub_dir
