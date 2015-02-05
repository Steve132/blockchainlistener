#!/usr/bin/env python

try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

P=['blockchainlistener','blockchainlistener.backends','blockchainlistener.backends.blockchain_info']

setup(name='blockchainlistener',
      version='0.8',
      description='Simple Blockchain Event Listener',
      author='Steven Braeger',
      author_email='Steve132@github.com',
      url='https://github.com/Steve132/blockchainlistener',
      packages=P,
      package_data={'blockchainlistener.backends.blockchain_info':['cacert.pem']},
      requires=['pybitcointools']
     )
