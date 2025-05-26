from setuptools import setup, find_packages

setup(
    name='debian-package-downloader',
    description='Debian package downloader that supports downloading packages from .deb file URL'
    'and .deb GitHub release asset',
    author='Ferenc Nandor Janky & Attila Gombos',
    author_email='info@effective-range.com',
    packages=find_packages(exclude=['tests']),
    scripts=['bin/debian-package-downloader.py'],
    package_data={'package_downloader': ['py.typed']},
    use_scm_version=True,
    setup_requires=["setuptools_scm"],
    install_requires=[
        'PyGithub',
        'requests',
        'pydantic',
        'python-context-logger@git+https://github.com/EffectiveRange/python-context-logger.git@latest',
        'python-common-utility@git+https://github.com/EffectiveRange/python-common-utility.git@latest',
    ],
)
