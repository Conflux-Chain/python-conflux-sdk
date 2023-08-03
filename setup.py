#!/usr/bin/env python
# -*- coding: utf-8 -*-
from setuptools import (
    find_packages,
    setup,
)

VERSION = "1.1.0"
DESCRIPTION = 'Python SDK for Conflux network'
with open('./README.md') as readme:
    long_description = readme.read()

extras_require = {
    'tester': [
        "docker>=6.0.0,<7",
        "pytest>=6.2.5,<7",
        "typing_extensions",
        "pytest-cov",
        "ipfshttpclient==0.8.0a2",
        "python-dotenv",
        # "py-geth>=3.8.0,<4",
    ],
    'linter': [
        "black>=22.1.0,<23.0",
        # "flake8==3.8.3",
        # "isort>=4.2.15,<4.3.5",
        # "mypy==0.910",
        # "types-setuptools>=57.4.4,<58",
        # "types-requests>=2.26.1,<3",
        # "types-protobuf==3.19.13",
    ],
    'docs': [
        # "mock",
        # "sphinx-better-theme>=0.1.4",
        # "click>=5.1",
        # "configparser==3.5.0",
        # "contextlib2>=0.5.4",
        # "py-geth>=3.8.0,<4",
        # "py-solc>=0.4.0",
        # "pytest>=6.2.5,<7",
        # "sphinx>=4.2.0,<5",
        "jupyter-book==0.11.3",
        # "sphinx_rtd_theme>=0.1.9",
        # "toposort>=1.4",
        # "towncrier==18.5.0",
        # "urllib3",
        "wheel"
    ],
    'dev': [
        # "bumpversion",
        # "flaky>=3.7.0,<4",
        # "hypothesis>=3.31.2,<6",
        # "pytest>=6.2.5,<7",
        # "pytest-asyncio>=0.18.1,<0.19",
        # "pytest-mock>=1.10,<2",
        # "pytest-pythonpath>=0.3",
        # "pytest-watch>=4.2,<5",
        # "pytest-xdist>=1.29,<2",
        # "setuptools>=38.6.0",
        # "tox>=1.8.0",
        # "tqdm>4.32,<5",
        # "twine>=1.13,<2",
        # "pluggy==0.13.1",
        # "when-changed>=0.3.0,<0.4"
    ],
    "ipfs": [
        "ipfshttpclient==0.8.0a2",
    ],
}

extras_require['dev'] = (
    extras_require['tester']
    + extras_require['linter']
    + extras_require['docs']
    # + extras_require["ipfs"] ipfs is included in tester
    + extras_require['dev']
)


# Setting up
setup(
    # the name must match the folder name 'verysimplemodule'
    name="conflux-web3",
    version=VERSION,
    author="Conflux-Dev",
    author_email="wenda.zhang@confluxnetwork.org",
    description=DESCRIPTION,
    long_description_content_type="text/markdown",
    long_description=long_description,
    packages=find_packages(),
    package_data={"conflux_web3": ["contract/metadata/*.json", "py.typed"],
                  "cns": ["py.typed"],
                  "cfxpm": ["py.typed"]},
    url='https://github.com/conflux-chain/python-conflux-sdk',
    install_requires=[
        "web3==6.2.0",
        "cfx-address>=1.0.0",
        "cfx-account>=1.0.0",
        "cfx-utils>=1.0.0",
        # "cached_property==1.5.2", # required by cfx-account
        # "eth-account>=0.6.0,<0.7.0"
    ],  # add any additional packages that
    # needs to be installed along with your package. Eg: 'caer'
    extras_require=extras_require,
    keywords=['python', 'conflux', 'blockchain'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Programming Language :: Python :: 3.11',
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
    ]
)
