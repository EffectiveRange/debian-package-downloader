import unittest
from typing import Optional
from unittest import TestCase
from unittest.mock import MagicMock

from common_utility import IFileDownloader
from context_logger import setup_logging
from github.GitRelease import GitRelease
from github.Repository import Repository

from package_downloader import IAssetDownloader, DebDownloader, PackageConfig, ReleaseConfig, IRepositoryProvider


class DebDownloaderTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('debian-package-downloader', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_returns_downloaded_file_path_when_download_from_file_url(self):
        # Given
        repository_provider, release_downloader, file_downloader = create_components()
        deb_downloader = DebDownloader(repository_provider, release_downloader, file_downloader)
        package_config = PackageConfig(package='package1', version='1.0.0', file_url='https://example.com/package1.deb')

        # When
        result = deb_downloader.download(package_config)

        # Then
        self.assertEqual('/opt/debs/package1.deb', result)
        file_downloader.download.assert_called_once_with(package_config.file_url)
        repository_provider.get_repository.assert_not_called()
        release_downloader.download.assert_not_called()

    def test_returns_downloaded_file_path_when_download_from_release(self):
        # Given
        repository = MagicMock(spec=Repository)
        release = MagicMock(spec=GitRelease)
        repository_provider, release_downloader, file_downloader = create_components(repository, release)
        deb_downloader = DebDownloader(repository_provider, release_downloader, file_downloader)
        release_config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='$TEST_TOKEN')
        package_config = PackageConfig(package='package2', version='1.0.0', release=release_config)

        # When
        result = deb_downloader.download(package_config)

        # Then
        self.assertEqual('/opt/debs/package2.deb', result)
        file_downloader.download.assert_not_called()
        repository_provider.get_repository.assert_called_once_with(release_config)
        repository.get_release.assert_called_once_with('v1.0.0')
        release_downloader.download.assert_called_once_with(release_config, release, first_match_only=True)

    def test_downloads_latest_when_download_from_release_and_not_tag_is_specified(self):
        # Given
        repository = MagicMock(spec=Repository)
        release = MagicMock(spec=GitRelease)
        repository_provider, release_downloader, file_downloader = create_components(repository, release)
        deb_downloader = DebDownloader(repository_provider, release_downloader, file_downloader)
        release_config = ReleaseConfig(owner='owner1', repo='repo1', matcher='*.deb')
        package_config = PackageConfig(package='package2', version='1.0.0', release=release_config)

        # When
        result = deb_downloader.download(package_config)

        # Then
        self.assertEqual('/opt/debs/package2.deb', result)
        file_downloader.download.assert_not_called()
        repository_provider.get_repository.assert_called_once_with(release_config)
        repository.get_latest_release.assert_called_once()
        release_downloader.download.assert_called_once_with(release_config, release, first_match_only=True)

    def test_raises_error_when_no_download_source_configured(self):
        # Given
        repository_provider, release_downloader, file_downloader = create_components()
        deb_downloader = DebDownloader(repository_provider, release_downloader, file_downloader)
        package_config = PackageConfig(package='package2', version='1.0.0')

        # When
        self.assertRaises(ValueError, deb_downloader.download, package_config)

        # Then
        file_downloader.download.assert_not_called()
        repository_provider.get_repository.assert_not_called()
        release_downloader.download.assert_not_called()

    def test_raises_error_when_download_from_release_and_release_not_found(self):
        # Given
        repository = MagicMock(spec=Repository)
        repository_provider, release_downloader, file_downloader = create_components(repository)
        deb_downloader = DebDownloader(repository_provider, release_downloader, file_downloader)
        release_config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')
        package_config = PackageConfig(package='package2', version='1.0.0', release=release_config)

        # When
        self.assertRaises(ValueError, deb_downloader.download, package_config)

        # Then
        repository_provider.get_repository.assert_called_once_with(release_config)
        repository.get_release.assert_called_once_with('v1.0.0')


def create_components(repository: Optional[Repository] = None, release: Optional[GitRelease] = None):
    if repository:
        repository.full_name = 'owner1/repo1'
        repository.get_release.return_value = release
        repository.get_latest_release.return_value = release

    if release:
        release.tag_name = 'v1.0.0'

    repository_provider = MagicMock(spec=IRepositoryProvider)
    repository_provider.get_repository.return_value = repository

    asset_downloader = MagicMock(spec=IAssetDownloader)
    asset_downloader.download.return_value = ['/opt/debs/package2.deb']

    file_downloader = MagicMock(spec=IFileDownloader)
    file_downloader.download.return_value = '/opt/debs/package1.deb'
    return repository_provider, asset_downloader, file_downloader


if __name__ == '__main__':
    unittest.main()
