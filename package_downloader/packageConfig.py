# SPDX-FileCopyrightText: 2024 Ferenc Nandor Janky <ferenj@effective-range.com>
# SPDX-FileCopyrightText: 2024 Attila Gombos <attila.gombos@effective-range.com>
# SPDX-License-Identifier: MIT

from typing import Optional

from pydantic import BaseModel

from package_downloader import ReleaseConfig


class PackageConfig(BaseModel):
    package: str
    version: Optional[str] = None
    file_url: Optional[str] = None
    release: Optional[ReleaseConfig] = None

    def __repr__(self) -> str:
        return (f'PackageConfig(package={self.package}, version={self.version}, '
                f'file_url={self.file_url}, release={self.release})')
