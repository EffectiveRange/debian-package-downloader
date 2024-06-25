import os
import unittest
from unittest import TestCase

from context_logger import setup_logging
from pydantic import ValidationError

from package_downloader import JsonLoader, PackageConfig
from tests import TEST_RESOURCE_ROOT


class JsonLoaderTest(TestCase):
    TEST_CONFIG_DIR = f'{TEST_RESOURCE_ROOT}/config'

    @classmethod
    def setUpClass(cls):
        setup_logging('debian-package-downloader', 'DEBUG', warn_on_overwrite=False)
        os.environ['TEST_TOKEN'] = 'test_token'

    def setUp(self):
        print()

    def test_returns_object_list_when_json_file_is_schema_valid(self):
        # Given
        json_loader = JsonLoader()

        # When
        config_list = json_loader.load_list(f'{self.TEST_CONFIG_DIR}/package-config.list.json', PackageConfig)

        # Then
        self.assertEqual(4, len(config_list))
        config_1 = config_list[0]
        self.assertEqual(config_1.package, 'package1')
        self.assertEqual(config_1.version, '1.0.0')
        self.assertIsNone(config_1.file_url)
        self.assertEqual(config_1.release.owner, 'owner1')
        self.assertEqual(config_1.release.repo, 'repo1')
        self.assertEqual(config_1.release.tag, 'v1.0.0')
        self.assertEqual(config_1.release.token, 'token1')
        self.assertEqual(config_1.release.get_token(), 'token1')
        self.assertEqual(config_1.release.matcher, '*.deb')
        config_2 = config_list[1]
        self.assertEqual(config_2.package, 'package2')
        self.assertEqual(config_2.version, '2.0.0')
        self.assertEqual(config_2.file_url, 'url2')
        self.assertIsNone(config_2.release)
        config_3 = config_list[2]
        self.assertEqual(config_3.package, 'package3')
        self.assertIsNone(config_3.version)
        self.assertIsNone(config_3.file_url)
        self.assertEqual(config_3.release.owner, 'owner3')
        self.assertEqual(config_3.release.repo, 'repo3')
        self.assertEqual(config_3.release.tag, 'v3.0.0')
        self.assertEqual(config_3.release.token, '$TEST_TOKEN')
        self.assertEqual(config_3.release.get_token(), 'test_token')
        self.assertEqual(config_3.release.matcher, '*.deb')
        config_4 = config_list[3]
        self.assertEqual(config_4.package, 'package4')
        self.assertIsNone(config_4.version)
        self.assertEqual(config_4.file_url, 'url4')
        self.assertEqual(config_4.release.owner, 'owner4')
        self.assertEqual(config_4.release.repo, 'repo4')
        self.assertEqual(config_4.release.tag, 'v4.0.0')
        self.assertIsNone(config_4.release.token)
        self.assertIsNone(config_4.release.get_token())
        self.assertEqual(config_4.release.matcher, '*.deb')

    def test_returns_object_when_json_file_is_schema_valid(self):
        # Given
        json_loader = JsonLoader()

        # When
        config = json_loader.load(f'{self.TEST_CONFIG_DIR}/package-config.single.json', PackageConfig)

        # Then
        self.assertEqual(config.package, 'package1')
        self.assertEqual(config.version, '1.0.0')
        self.assertIsNone(config.file_url)
        self.assertEqual(config.release.owner, 'owner1')
        self.assertEqual(config.release.repo, 'repo1')
        self.assertEqual(config.release.tag, 'v1.0.0')
        self.assertEqual(config.release.token, 'token1')
        self.assertEqual(config.release.get_token(), 'token1')
        self.assertEqual(config.release.matcher, '*.deb')

    def test_returns_object_when_json_string_is_schema_valid(self):
        # Given
        json_loader = JsonLoader()

        # When
        config = json_loader.load('''
        {
          "package": "package1",
          "version": "1.0.0",
          "release": {
            "owner": "owner1",
            "repo": "repo1",
            "tag": "v1.0.0",
            "token": "token1",
            "matcher": "*.deb"
          }
        }
        ''', PackageConfig)

        # Then
        self.assertEqual(config.package, 'package1')
        self.assertEqual(config.version, '1.0.0')
        self.assertIsNone(config.file_url)
        self.assertEqual(config.release.owner, 'owner1')
        self.assertEqual(config.release.repo, 'repo1')
        self.assertEqual(config.release.tag, 'v1.0.0')
        self.assertEqual(config.release.token, 'token1')
        self.assertEqual(config.release.get_token(), 'token1')
        self.assertEqual(config.release.matcher, '*.deb')

    def test_raises_error_when_json_file_is_schema_invalid(self):
        # Given
        json_loader = JsonLoader()

        # When
        self.assertRaises(ValidationError, json_loader.load_list, f'{self.TEST_CONFIG_DIR}/package-config.invalid.json',
                          PackageConfig)

        # Then
        # Exception is raised

    def test_raises_error_when_root_type_is_invalid(self):
        # Given
        json_loader = JsonLoader()

        # When
        self.assertRaises(ValueError, json_loader.load, f'{self.TEST_CONFIG_DIR}/package-config.list.json',
                          PackageConfig)

        # Then
        # Exception is raised


if __name__ == '__main__':
    unittest.main()
