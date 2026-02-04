import os
import unittest
from unittest import TestCase

from context_logger import setup_logging

from package_downloader import ReleaseConfig


class ReleaseConfigTest(TestCase):

    @classmethod
    def setUpClass(cls):
        setup_logging('debian-package-downloader', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()

    def test_returns_full_name(self):
        # Given
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')

        full_name = config.full_name

        # Then
        self.assertEqual('owner1/repo1', full_name)

    def test_returns_is_private_when_not_set(self):
        # Given
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')

        is_private = config.is_private

        # Then
        self.assertFalse(is_private)

    def test_returns_is_private_when_true(self):
        # Given
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1',
                               private=True)

        is_private = config.is_private

        # Then
        self.assertTrue(is_private)

    def test_returns_is_private_when_false(self):
        # Given
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1',
                               private=False)

        is_private = config.is_private

        # Then
        self.assertFalse(is_private)

    def test_returns_raw_token(self):
        # Given
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='token1')

        token = config.raw_token

        # Then
        self.assertEqual('token1', token)

    def test_returns_raw_token_when_env_variable(self):
        # Given
        os.environ['TEST_TOKEN'] = 'token1'
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='$TEST_TOKEN')

        token = config.raw_token

        # Then
        self.assertEqual('token1', token)

    def test_returns_raw_token_when_env_variable_with_curly_braces(self):
        # Given
        os.environ['TEST_TOKEN'] = 'token1'
        config = ReleaseConfig(owner='owner1', repo='repo1', tag='v1.0.0', matcher='*.deb', token='${TEST_TOKEN}')

        token = config.raw_token

        # Then
        self.assertEqual('token1', token)


if __name__ == '__main__':
    unittest.main()
