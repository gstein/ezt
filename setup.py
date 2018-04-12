#!/usr/bin/env python
"""setup"""

import os
import distutils.core

# patch distutils if it can't cope with the "classifiers" or
# "download_url" keywords
from sys import version
if version < '2.2.3':
    import distutils.dist
    distutils.dist.DistributionMetadata.classifiers = None
    distutils.dist.DistributionMetadata.download_url = None

for line in open(os.path.join(os.path.dirname(__file__), 'ezt.py')):
    if line.startswith('__version__'):
        version = eval(line.split('=')[-1])
        break

distutils.core.setup(
    name='ezt',
    version=version,
    description='EaZy Templating for Python.',
    long_description='EZT is a lightweight, fast, and safe templating system for Python. It is useful for generating HTML, plain text, code, and more.',
    author='Greg Stein',
    author_email='gstein@gmai.com',
    url='http://code.google.com/p/ezt/',
    py_modules=['ezt'],
    license='BSD',
    platforms='any',
    classifiers=[
        'Development Status :: 6 - Mature',
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: BSD License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Code Generators',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
        'Topic :: Internet :: WWW/HTTP :: WSGI',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Application',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Middleware',
        'Topic :: Internet :: WWW/HTTP :: WSGI :: Server',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Pre-processors',
        'Programming Language :: Python :: 2',
        'Topic :: Text Processing',
    ],
)
