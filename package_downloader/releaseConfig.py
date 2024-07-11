# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import os
from typing import Optional

from pydantic import BaseModel


class ReleaseConfig(BaseModel):
    owner: str
    repo: str
    matcher: str = '*'
    tag: Optional[str] = None
    token: Optional[str] = None

    def __repr__(self) -> str:
        tag = f'@{self.tag}' if self.tag else ''
        has_token = self.raw_token is not None
        return f'ReleaseConfig({self.full_name}.git{tag}, matcher={self.matcher}, has_token={has_token})'

    @property
    def raw_token(self) -> Optional[str]:
        if self.token and self.token.startswith('$'):
            return os.getenv(self.token[1:], None)
        return self.token

    @property
    def full_name(self) -> str:
        return f'{self.owner}/{self.repo}'
