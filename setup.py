#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

VERSION = '0.0.2'
DESCRIPTION = 'The python conflux SDK'

with open("readme.md", "r") as fh:
    long_description = fh.read()

# Setting up
setup(
       # the name must match the folder name 'verysimplemodule'
        name="conflux",
        version=VERSION,
        author="Conflux-Dev",
        author_email="wangpan@conflux-chain.org",
        description=DESCRIPTION,
        long_description=long_description,
        packages=find_packages(),
        install_requires=[
            # "eth-account>=0.5.3,<0.6.0",
            "web3>=5.14",
            "cfx-address",
            "cfx-account"
        ], # add any additional packages that
        # needs to be installed along with your package. Eg: 'caer'
        
        keywords=['python', 'conflux', 'blockchain'],
        classifiers= [
            "Programming Language :: Python :: 3",
            "Operating System :: MacOS :: MacOS X",
            "Operating System :: Microsoft :: Windows",
        ]
)
