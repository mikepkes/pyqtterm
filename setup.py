#!/usr/bin/env python
"""
Copyright (c) 2014, Michael Kessler
All rights reserved.

Redistribution and use in source and binary forms, with or without
modification, are permitted provided that the following conditions are met:

* Redistributions of source code must retain the above copyright notice, this
  list of conditions and the following disclaimer.

* Redistributions in binary form must reproduce the above copyright notice,
  this list of conditions and the following disclaimer in the documentation
  and/or other materials provided with the distribution.

THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS"
AND ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE
FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER
CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY,
OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.

"""

# ==============================================================================
# IMPORTS
# ==============================================================================

from setuptools import setup, find_packages
import codecs
import os
import re

# ==============================================================================
# GLOBALS
# ==============================================================================

HERE = os.path.abspath(os.path.dirname(__file__))
MAIN_FILE = os.path.join(HERE, 'qtterm', '__init__.py')

# Get the long description from the relevant file
with codecs.open('README.rst', encoding='utf-8') as readme_file:
    LONG_DESCRIPTION = readme_file.read()

# ==============================================================================
# PRIVATE FUNCTIONS
# ==============================================================================


def _find_metadata(filepath):
    """Reads all the metadata from a source file by opening manually.

    Why open and read it and not import?

    https://groups.google.com/d/topic/pypa-dev/0PkjVpcxTzQ/discussion

    Args:
        filepath : (str)
            Filepath to the file containing the metadata.

    Returns:
        {str: str}
            Dictionary with metadata keys and values.

    Raises:
        RuntimeError
            Cannot proceed if version or module_name not found

    """
    # Open in Latin-1 so that we avoid encoding errors.
    # Use codecs.open for Python 2 compatibility
    with codecs.open(filepath, 'r', 'latin1') as meta_file:
        metadata_file = meta_file.read()

    metadata = {}

    version_match = re.search(r"^__version__ = ['\"]([^'\"]*)['\"]",
                              metadata_file, re.M)
    author_match = re.search(r"^__author__ = ['\"]([^'\"]*)['\"]",
                             metadata_file, re.M)
    author_email_match = re.search(r"^__author_email__ = ['\"]([^'\"]*)['\"]",
                             metadata_file, re.M)
    copyright_match = re.search(r"^__copyright__ = ['\"]([^'\"]*)['\"]",
                                metadata_file, re.M)
    credits_match = re.search(r"^__credits__ = ['\"]([^'\"]*)['\"]",
                              metadata_file, re.M)
    license_match = re.search(r"^__license__ = ['\"]([^'\"]*)['\"]",
                              metadata_file, re.M)
    maint_match = re.search(r"^__maintainer__ = ['\"]([^'\"]*)['\"]",
                            metadata_file, re.M)
    maint_email_match = re.search(r"^__maintainer_email__ = ['\"]([^'\"]*)['\"]",
                            metadata_file, re.M)
    module_name_match = re.search(r"^__module_name__ = ['\"]([^'\"]*)['\"]",
                            metadata_file, re.M)
    short_desc_match = re.search(r"^__short_desc__ = ['\"]([^'\"]*)['\"]",
                             metadata_file, re.M)
    status_match = re.search(r"^__status__ = ['\"]([^'\"]*)['\"]",
                             metadata_file, re.M)
    url_match = re.search(r"^__url__ = ['\"]([^'\"]*)['\"]",
                             metadata_file, re.M)

    if not version_match or not module_name_match:
        raise RuntimeError("Unable to find version or module_name string.")

    if author_match:
        metadata['author'] = author_match.group(1)
    if author_email_match:
        metadata['author_email'] = author_email_match.group(1)
    if copyright_match:
        metadata['copyright'] = copyright_match.group(1)
    if credits_match:
        metadata['credits'] = credits_match.group(1)
    if license_match:
        metadata['license'] = license_match.group(1)
    if maint_match:
        metadata['maintainer'] = maint_match.group(1)
    if maint_email_match:
        metadata['maintainer_email'] = maint_email_match.group(1)
    if module_name_match:
        metadata['module_name'] = module_name_match.group(1)
    if short_desc_match:
        metadata['short_desc'] = short_desc_match.group(1)
    if status_match:
        metadata['status'] = status_match.group(1)
    if version_match:
        metadata['version'] = version_match.group(1)
    if url_match:
        metadata['url'] = url_match.group(1)

    return metadata

# ==============================================================================
# MAIN
# ==============================================================================

metadata = _find_metadata(MAIN_FILE)

setup(
    name=metadata['module_name'],
    version=metadata['version'],
    description=metadata.get('short_desc', ''),
    long_description=LONG_DESCRIPTION,

    # The project URL.
    url=metadata.get('url', 'http://www.github.com/mikepkes/pyqtterm'),

    # Author & Maintainer details
    author=metadata.get('author', 'Michael Kessler'),
    author_email=metadata.get('author_email', 'mike@toadgrass.com'),
    maintainer=metadata.get('maintainer', 'Michael Kessler'),
    maintainer_email=metadata.get('maintainer_email', 'mike@toadgrass.com'),

    license=metadata.get('license', 'Simplified BSD'),

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 1 - Planning',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Libraries :: Python Modules',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: BSD License',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python :: 2.6',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',

        # OS
        'Operating System :: OS Independent',

        # Language
        'Natural Language :: English',
    ],

    # What does your project relate to?
    keywords='qt terminal',

    # You can just specify the packages manually here if your project is
    # simple. Or you can use find_packages.
    packages=find_packages(exclude=['tests']),

    # List run-time dependencies here. These will be installed by pip when your
    # project is installed.
    #install_requires=['PySide'],
    #TODO: Make requirements PySide OR PyQt to allow for greater flexibility.
    install_requires=[],

    # If there are data files included in your packages that need to be
    # installed, specify them here.  If using Python 2.6 or less, then these
    # have to be included in MANIFEST.in as well.
    package_data={},
    include_package_data=True,

    # Targeted OS
    platforms='any',

    # To provide executable scripts, use entry points in preference to the
    # "scripts" keyword. Entry points provide cross-platform support and allow
    # pip to create the appropriate form of executable for the target platform.
    entry_points={
        'console_scripts': [
            'qtterm=qtterm:main',
        ],
    },

)
