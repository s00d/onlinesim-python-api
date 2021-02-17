from os import path
from setuptools import setup

"""
@author: s00d
@contact: https://github.com/s00d
@license Apache License, Version 2.0, see LICENSE file
Copyright (C) 2020
"""


def long_description():
    """Build the description from README file """
    this_dir = path.abspath(path.dirname(__file__))
    with open(path.join(this_dir, "README.md")) as f:
        return f.read()


def requirements():
    """Build the requirements list for this project"""
    requirements_list = list()
    with open("requirements.txt") as pc_requirements:
        for install in pc_requirements:
            requirements_list.append(install.strip())
    return requirements_list


setup(
    name="onlinesimru",
    version="1.0.9",
    long_description=long_description(),
    long_description_content_type="text/markdown",
    description="Wrapper for automatic reception of SMS-messages by onlinesim.ru",
    author="s00d",
    license="Apache License, Version 2.0, see LICENSE file",
    keywords="sms, revice, onlinesim-ru, autoreg",
    author_email="suppport@onlinesim.ru",
    url="https://github.com/s00d/onlinesim-python-api",
    download_url="https://github.com/s00d/onlinesim-python-api/archive/master.zip",
    packages=["onlinesimru"],
    install_requires=requirements(),
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Environment :: Console",
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: PyPy",
    ],
)
