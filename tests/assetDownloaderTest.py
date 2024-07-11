import unittest
from unittest import TestCase, mock
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

    def test_returns_downloaded_files_paths_when_assets_found(self):
        # Given
        file_downloader, release = create_components(['/opt/debs/package1.deb', '/opt/debs/package2.deb'])
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')

        # When
        result = asset_downloader.download(config, release, skip_if_exists=False)

        # Then
        self.assertEqual(2, len(result))
        self.assertEqual('/opt/debs/package1.deb', result[0])
        self.assertEqual('/opt/debs/package2.deb', result[1])
        file_downloader.download.assert_has_calls([
            mock.call('url2', 'package1.deb', {'Accept': 'application/octet-stream', 'Authorization': 'token token1'}),
            mock.call('url3', 'package2.deb', {'Accept': 'application/octet-stream', 'Authorization': 'token token1'})
        ])

    def test_returns_downloaded_file_path_when_assets_founds_and_no_token_specified(self):
        # Given
        file_downloader, release = create_components(['/opt/debs/package1.deb', '/opt/debs/package2.deb'])
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb')

        # When
        result = asset_downloader.download(config, release)

        # Then
        self.assertEqual(2, len(result))
        self.assertEqual('/opt/debs/package1.deb', result[0])
        self.assertEqual('/opt/debs/package2.deb', result[1])
        file_downloader.download.assert_has_calls([
            mock.call('url2', 'package1.deb', {'Accept': 'application/octet-stream'}),
            mock.call('url3', 'package2.deb', {'Accept': 'application/octet-stream'})
        ])

    def test_downloads_all_files_when_no_matcher_is_specified(self):
        # Given
        file_downloader, release = create_components(
            ['/opt/debs/package1.whl', '/opt/debs/package1.deb', '/opt/debs/package2.deb'])
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', token='token1')

        # When
        result = asset_downloader.download(config, release, skip_if_exists=False)

        # Then
        self.assertEqual(3, len(result))
        self.assertEqual('/opt/debs/package1.whl', result[0])
        self.assertEqual('/opt/debs/package1.deb', result[1])
        self.assertEqual('/opt/debs/package2.deb', result[2])
        file_downloader.download.assert_has_calls([
            mock.call('url1', 'package1.whl', {'Accept': 'application/octet-stream', 'Authorization': 'token token1'}),
            mock.call('url2', 'package1.deb', {'Accept': 'application/octet-stream', 'Authorization': 'token token1'}),
            mock.call('url3', 'package2.deb', {'Accept': 'application/octet-stream', 'Authorization': 'token token1'})
        ])

    def test_returns_downloaded_file_path_when_asset_found_and_first_match_only(self):
        # Given
        file_downloader, release = create_components(['/opt/debs/package1.deb'])
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')

        # When
        result = asset_downloader.download(config, release, first_match_only=True, skip_if_exists=False)

        # Then
        self.assertEqual('/opt/debs/package1.deb', result[0])
        file_downloader.download.assert_called_once_with(
            'url2', 'package1.deb', {'Accept': 'application/octet-stream', 'Authorization': 'token token1'})

    def test_raises_error_when_asset_not_found(self):
        # Given
        file_downloader, release = create_components()
        asset_downloader = AssetDownloader(file_downloader)
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.tar.gz', token='token1')

        # When
        self.assertRaises(ValueError, asset_downloader.download, config, release)

        # Then
        # Error raised


def create_components(downloaded_files=None):
    if downloaded_files is None:
        downloaded_files = []
    file_downloader = MagicMock(spec=IFileDownloader)
    file_downloader.download.side_effect = downloaded_files
    release = MagicMock(spec=GitRelease)
    asset1 = MagicMock(spec=GitReleaseAsset)
    asset1.name = 'package1.whl'
    asset1.url = 'url1'
    asset2 = MagicMock(spec=GitReleaseAsset)
    asset2.name = 'package1.deb'
    asset2.url = 'url2'
    asset3 = MagicMock(spec=GitReleaseAsset)
    asset3.name = 'package2.deb'
    asset3.url = 'url3'
    release.get_assets.return_value = [asset1, asset2, asset3]

    return file_downloader, release


if __name__ == '__main__':
    unittest.main()
