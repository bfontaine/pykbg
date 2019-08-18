# -*- coding: UTF-8 -*-

from setuptools import setup

setup(
    name='kbg',
    version='0.0.1',
    author='Baptiste Fontaine',
    author_email='b@ptistefontaine.fr',
    url='https://github.com/bfontaine/pykbg',
    license='MIT License',
    description='Python wrapper for the Kelbongoo website',
    long_description=open('README.md', 'r', encoding='utf-8').read(),
    long_description_content_type='text/markdown',
    install_requires=[
        'requests',
    ],
    classifiers=[
        'Environment :: Console',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
