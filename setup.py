#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

VERSION = '0.0.6'
DESCRIPTION = 'Conflux\'s python  SDK'
LONG_DESCRIPTION = 'A Python SDK for interacting with Conflux network, check details here https://github.com/conflux-chain/python-conflux-sdk'

# with open("readme.md", "r") as fh:
#     long_description = fh.read()

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="conflux",
        version=VERSION,
        author="Conflux-Dev",
        author_email="wangpan@conflux-chain.org",
        description=DESCRIPTION,
        long_description=LONG_DESCRIPTION,
        packages=find_packages(),
        install_requires=[
            "web3>=5.14.0,<=5.17.0",
            "cfx-address>=0.0.3",
            "cfx-account>=0.0.1",
            "eth-tester>=0.5.0b4"
        ], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'conflux', 'blockchain'],
        classifiers= [
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
