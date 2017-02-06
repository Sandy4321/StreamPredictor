# -*- coding: utf-8 -*-

from setuptools import setup, find_packages


setup(
    name='streampredictor',
    version='0.0.1',
    description='Model sequential data',
    author='Abhishek Rao',
    author_email='abhishek.rao.comm@gmail.com',
    url='https://github.com/abhishekraok/StreamPredictor',
    download_url='https://github.com/abhishekraok/StreamPredictor/archive/v0.0.1.tar.gz',
    packages=find_packages(exclude=('docs'))
)

