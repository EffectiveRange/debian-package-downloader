from setuptools import setup

setup(
    name='debian-package-downloader',
    version='1.1.0',
    description='Debian package downloader that supports downloading packages from .deb file URL'
    'and .deb GitHub release asset',
    author='Ferenc Nandor Janky & Attila Gombos',
    author_email='info@effective-range.com',
    packages=['package_downloader'],
    scripts=['bin/debian-package-downloader.py'],
    package_data={'package_downloader': ['py.typed']},
    install_requires=[
        'PyGithub',
        'requests',
        'pydantic',
        'python-context-logger@git+https://github.com/EffectiveRange/python-context-logger.git@latest',
        'python-common-utility@git+https://github.com/EffectiveRange/python-common-utility.git@latest',
    ],
)
