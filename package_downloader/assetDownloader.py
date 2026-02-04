# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import fnmatch
from collections import OrderedDict
from pathlib import Path

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

    def __init__(self, file_downloader: IFileDownloader, distro_map: OrderedDict[str, str] | None = None,
                 private_dir: Path = Path('private')) -> None:
        self._file_downloader = file_downloader
        self._distro_map: OrderedDict[str, str] = distro_map if distro_map else OrderedDict()
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
                    downloaded_files.extend(self._download_for_distro(asset, headers, config))
                else:
                    downloaded_files.append(self._download(asset.url, asset.name, None, headers, config))

                if first_match_only:
                    break

        if not downloaded_files:
            log.error('No matching asset found', release=config, assets=[asset.name for asset in assets])
            raise ValueError('No matching asset found')

        return downloaded_files

    def _download_for_distro(self, asset: GitReleaseAsset, headers: dict[str, str],
                             config: ReleaseConfig) -> list[Path]:
        for distro_matcher, distro_dir in self._distro_map.items():
            if distro_matcher in asset.name:
                return [self._download(asset.url, asset.name, Path(distro_dir), headers, config)]

        return self._download_and_copy(asset.url, asset.name, headers, config)

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
    def _download(self, url: str, filename: str, distro_dir: Path | None, headers: dict[str, str],
                  config: ReleaseConfig) -> Path:
        sub_dir = self._get_sub_dir(distro_dir, config) if distro_dir or config.private else None
        return self._file_downloader.download(url, filename, sub_dir, headers)

    @retry(wait=wait_fixed(1), stop=stop_after_attempt(3), reraise=True)
    def _download_and_copy(self, url: str, filename: str, headers: dict[str, str], config: ReleaseConfig) -> list[Path]:
        sub_dirs: list[str | Path] = [
            self._get_sub_dir(Path(distro_dir), config) for distro_dir in self._distro_map.values()
        ]
        return self._file_downloader.download_and_copy(url, sub_dirs, filename, headers)

    def _get_sub_dir(self, distro_dir: Path | None, config: ReleaseConfig) -> Path:
        if distro_dir:
            component_dir = distro_dir / config.component
            return component_dir / self._private_dir if config.private else component_dir
        else:
            return self._private_dir if config.private else Path()
