import unittest
from unittest import TestCase
from unittest.mock import MagicMock

from context_logger import setup_logging
from requests import Session, Response

from package_downloader import ISessionProvider, FileDownloader
from tests import TEST_FILE_SYSTEM_ROOT, delete_directory, create_directory


class FileDownloaderTest(TestCase):
    DOWNLOAD_LOCATION = f'{TEST_FILE_SYSTEM_ROOT}/opt/debs'

    @classmethod
    def setUpClass(cls):
        setup_logging('debian-package-downloader', 'DEBUG', warn_on_overwrite=False)

    def setUp(self):
        print()
        delete_directory(self.DOWNLOAD_LOCATION)

    def test_download_returns_downloaded_file_path(self):
        # Given
        session, session_provider = create_components()
        file_downloader = FileDownloader(session_provider, self.DOWNLOAD_LOCATION)

        # When
        result = file_downloader.download('url1/package1.deb')

        # Then
        session.get.assert_called_once_with('url1/package1.deb', stream=True, headers={})
        self.assertEqual(f'{self.DOWNLOAD_LOCATION}/package1.deb', result)
        with open(f'{self.DOWNLOAD_LOCATION}/package1.deb', 'rb') as file:
            self.assertEqual(b'content', file.read())

    def test_download_returns_downloaded_file_path_when_file_name_specified(self):
        # Given
        create_directory(self.DOWNLOAD_LOCATION)
        session, session_provider = create_components()
        file_downloader = FileDownloader(session_provider, self.DOWNLOAD_LOCATION)

        # When
        result = file_downloader.download('url1/package1.deb', 'test_package1.deb')

        # Then
        session.get.assert_called_once_with('url1/package1.deb', stream=True, headers={})
        self.assertEqual(f'{self.DOWNLOAD_LOCATION}/test_package1.deb', result)
        with open(f'{self.DOWNLOAD_LOCATION}/test_package1.deb', 'rb') as file:
            self.assertEqual(b'content', file.read())

    def test_download_returns_downloaded_file_path_when_headers_specified(self):
        # Given
        file_content = b'content'
        session, session_provider = create_components(content=file_content)
        file_downloader = FileDownloader(session_provider, self.DOWNLOAD_LOCATION)

        # When
        result = file_downloader.download('url1/package1.deb', headers={'header1': 'value1', 'header2': 'value2'})

        # Then
        session.get.assert_called_once_with('url1/package1.deb', stream=True,
                                            headers={'header1': 'value1', 'header2': 'value2'})
        self.assertEqual(f'{self.DOWNLOAD_LOCATION}/package1.deb', result)
        with open(f'{self.DOWNLOAD_LOCATION}/package1.deb', 'rb') as file:
            self.assertEqual(file_content, file.read())

    def test_raises_error_when_fails_to_download_file(self):
        # Given
        session, session_provider = create_components(401, 'Unauthorized')
        file_downloader = FileDownloader(session_provider, self.DOWNLOAD_LOCATION)

        # When
        self.assertRaises(ValueError, file_downloader.download, 'url1/package1.deb')

        # Then
        # Exception raised

    def test_download_returns_downloaded_file_path_when_file_is_present(self):
        # Given
        session, session_provider = create_components()
        file_downloader = FileDownloader(session_provider, self.DOWNLOAD_LOCATION)
        file_downloader.download('url1/package1.deb')
        session.reset_mock()

        # When
        result = file_downloader.download('url1/package1.deb')

        # Then
        session.get.assert_not_called()
        self.assertEqual(f'{self.DOWNLOAD_LOCATION}/package1.deb', result)

    def test_download_returns_downloaded_file_path_when_file_is_present_and_overwrites(self):
        # Given
        session, session_provider = create_components()
        file_downloader = FileDownloader(session_provider, self.DOWNLOAD_LOCATION)
        file_downloader.download('url1/package1.deb')
        session.reset_mock()

        # When
        result = file_downloader.download('url1/package1.deb', skip_if_exists=False)

        # Then
        session.get.assert_called_once_with('url1/package1.deb', stream=True, headers={})
        self.assertEqual(f'{self.DOWNLOAD_LOCATION}/package1.deb', result)


def create_components(status_code: int = 200, reason: str = 'OK', content: bytes = b'content'):
    response = MagicMock(spec=Response)
    response.status_code = status_code
    response.reason = reason
    response.iter_content.return_value = [content]
    session = MagicMock(spec=Session)
    session.get.return_value = response
    session_provider = MagicMock(spec=ISessionProvider)
    session_provider.get_session().__enter__.return_value = session
    return session, session_provider


if __name__ == '__main__':
    unittest.main()
