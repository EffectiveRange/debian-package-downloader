# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

from context_logger import get_logger
from github import Github
from github.Auth import Token
from github.Repository import Repository

from package_downloader import ReleaseConfig

log = get_logger('RepositoryProvider')


class IRepositoryProvider(object):

    def get_repository(self, release_config: ReleaseConfig) -> Repository:
        raise NotImplementedError()


class RepositoryProvider(IRepositoryProvider):

    def get_repository(self, config: ReleaseConfig) -> Repository:
        repo_name = f'{config.owner}/{config.repo}'

        try:
            token = config.get_token()
            auth = Token(token) if token else None
            return Github(auth=auth).get_repo(repo_name)
        except Exception as error:
            log.error('Error while getting repository', error=error, repository=repo_name)
            raise error
