#!/usr/bin/env python
"""
py2app/py2exe build script for Loxodo.

Usage (Mac OS X):
    python setup.py py2app

Usage (Windows):
    python setup.py py2exe
"""

import sys
import re
from setuptools import setup

version_regex = r'__version__ = ["\']([^"\']*)["\']'
with open('loxodo/__init__.py', 'r') as f:
    text = f.read()
    match = re.search(version_regex, text)

    if match:
        VERSION = match.group(1)
    else:
        raise RuntimeError("No version number found!")

if sys.platform == 'darwin':
    extra_options = dict(
        name="Loxodo",
        version=VERSION,
        setup_requires = ['py2app'],
        app = ['loxodo.py'],
        options = dict(
            py2app = dict(
                argv_emulation = False,
                iconfile = 'resources/loxodo-icon.icns',
                packages = ['loxodo', 'wx'],
                site_packages = True,
                resources = ['resources', 'locale', 'LICENSE.txt', 'README.txt']
            )
        )
    )
elif sys.platform == 'win32':
    import py2exe
    import os

    # create list of needed data files
    dataFiles = []
    for subdir in ('resources', 'locale'):
        for root, dirs, files in os.walk(subdir):
            if not files:
                next
            files = []
            for filename in files:
                files.append(os.path.join(root, filename))
            if not files:
                next
            dataFiles.append((root, files))

    extra_options = dict(
        version=VERSION,
        setup_requires = ['py2exe'],
        windows = ['loxodo.py'],
        data_files = dataFiles,
        options = dict(
            py2exe = dict(
                excludes = 'ppygui'
            )
        )
    )
else:
    extra_options = dict(
        name = 'loxodo',
        version=VERSION,
        author = 'Christoph Sommer',
        author_email = 'mail@christoph-sommer.de',
        url = 'http://www.christoph-sommer.de/loxodo/',
        description = 'A Password Safe V3 compatible password vault',
        download_url = 'http://github.com/sommer/loxodo/zipball/master',
        license = 'GPL-2.0+',
        entry_points = {
            'console_scripts': [
                'loxodo = loxodo.__main__:main']},
        packages = ['loxodo',
                    'loxodo.frontends',
                    'loxodo.frontends.wx',
                    'loxodo.twofish'],
        package_data = {
            'loxodo': [
                'resources/*',
                'locale/de/LC_MESSAGES/*'
            ],
        },
    )

setup(**extra_options)
