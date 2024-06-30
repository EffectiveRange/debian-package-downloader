# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

import os
from typing import Optional

from pydantic import BaseModel


class ReleaseConfig(BaseModel):
    owner: str
    repo: str
    tag: str
    matcher: str
    token: Optional[str] = None

    def __repr__(self) -> str:
        return (f'ReleaseConfig({self.owner}/{self.repo}.git@{self.tag}, '
                f'matcher={self.matcher}, has_token={self.token is not None})')

    def get_token(self) -> Optional[str]:
        if self.token and self.token.startswith('$'):
            return os.getenv(self.token[1:], None)
        return self.token
