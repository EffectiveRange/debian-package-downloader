import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from context_logger import setup_logging
from github.GitRelease import GitRelease
from github.GitReleaseAsset import GitReleaseAsset

from package_downloader import IFileDownloader, AssetDownloader, ReleaseConfig


class AssetDownloaderTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('debian-package-downloader', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_returns_downloaded_file_path_when_asset_found(self):
        # Given
        file_downloader, release = create_components()
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')

        # When
        result = asset_downloader.download(config, release, skip_if_exists=False)

        # Then
        self.assertEqual('/opt/debs/package1.deb', result)
        file_downloader.download.assert_called_once_with(
            'url2', 'package1.deb', {'Accept': 'application/octet-stream', 'Authorization': 'token token1'})

    def test_returns_downloaded_file_path_when_asset_found_and_no_token_specified(self):
        # Given
        file_downloader, release = create_components()
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb')

        # When
        result = asset_downloader.download(config, release)

        # Then
        self.assertEqual('/opt/debs/package1.deb', result)
        file_downloader.download.assert_called_once_with('url2', 'package1.deb', {'Accept': 'application/octet-stream'})

    def test_raises_error_when_asset_not_found(self):
        # Given
        file_downloader, release = create_components('package1.tar.gz')
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')

        # When
        self.assertRaises(ValueError, asset_downloader.download, config, release)

        # Then
        # Error raised


def create_components(asset_name: str = 'package1.deb'):
    file_downloader = MagicMock(spec=IFileDownloader)
    file_downloader.download.return_value = '/opt/debs/package1.deb'
    release = MagicMock(spec=GitRelease)
    asset1 = MagicMock(spec=GitReleaseAsset)
    asset1.name = 'package1.whl'
    asset1.url = 'url1'
    asset2 = MagicMock(spec=GitReleaseAsset)
    asset2.name = asset_name
    asset2.url = 'url2'
    release.get_assets.return_value = [asset1, asset2]

    return file_downloader, release


if __name__ == '__main__':
    unittest.main()
