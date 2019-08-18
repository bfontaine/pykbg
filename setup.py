# -*- coding: UTF-8 -*-

from setuptools import setup

# http://stackoverflow.com/a/7071358/735926
import re
VERSIONFILE='kbg/__init__.py'
verstrline = open(VERSIONFILE, 'rt').read()
VSRE = r'^__version__\s+=\s+[\'"]([^\'"]+)[\'"]'
mo = re.search(VSRE, verstrline, re.M)
if mo:
    verstr = mo.group(1)
else:
    raise RuntimeError("Unable to find version string in %s." % VERSIONFILE)

setup(
    name='kbg',
    version=verstr,
    author='Baptiste Fontaine',
    author_email='b@ptistefontaine.fr',
    url='https://github.com/bfontaine/pykbg',
    license='MIT License',
    description='Python wrapper for the Kelbongoo website',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    packages=['kbg'],
    install_requires=[
        'requests',
    ],
    extra_require={
        'dev': ['responses'],
    },
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
    python_requires='>=3.5',
)
