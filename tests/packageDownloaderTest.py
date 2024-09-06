import unittest
from unittest import TestCase, mock
from unittest.mock import MagicMock

from common_utility import IJsonLoader
from context_logger import setup_logging

from package_downloader import PackageDownloader, IDebDownloader, PackageConfig


class PackageDownloaderTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('debian-package-downloader', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_downloads_all_packages(self):
        # Given
        config1 = PackageConfig(package='package1', version='1.0.0')
        config2 = PackageConfig(package='package2', version='2.0.0')
        json_loader, deb_downloader = create_components([config1, config2])
        package_downloader = PackageDownloader('path/to/config', json_loader, deb_downloader)

        # When
        package_downloader.download_packages()

        # Then
        deb_downloader.download.assert_has_calls([mock.call(config1), mock.call(config2)])

    def test_downloads_only_one_package(self):
        # Given
        config1 = PackageConfig(package='package1', version='1.0.0')
        config2 = PackageConfig(package='package2', version='2.0.0')
        json_loader, deb_downloader = create_components([config1, config2])
        deb_downloader.download.side_effect = ['/opt/debs/package1', Exception('Failed to download package')]
        package_downloader = PackageDownloader('path/to/config', json_loader, deb_downloader)

        # When
        package_downloader.download_packages()

        # Then
        deb_downloader.download.assert_has_calls([mock.call(config1), mock.call(config2)])


def create_components(packages):
    config_loader = MagicMock(spec=IJsonLoader)
    config_loader.load_list.return_value = packages
    deb_downloader = MagicMock(spec=IDebDownloader)
    return config_loader, deb_downloader


if __name__ == '__main__':
    unittest.main()
