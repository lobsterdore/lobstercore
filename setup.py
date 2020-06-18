"""Lobstercore module
"""

from setuptools import setup, find_packages
from codecs import open
from os import path

here = path.abspath(path.dirname(__file__))

with open(path.join(here, "README.rst"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="lobstercore",
    description="Lobstercore module",
    long_description=long_description,
    url="https://github.com/lobsterdore/lobstercore",
    author="David Reed",
    author_email="dreed@mail.techpunch.co.uk",
    license="MIT",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Build Tools",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3.7",
    ],
    keywords="lobsterdore",
    packages=["lobstercore", "lobstercore.search"],
    install_requires=[
        "PyMySQL==0.9.3",
        "SQLAlchemy>=0.9.4",
        "Flask-ini>=0.2.1",
        "elasticsearch>=7.5.1",
    ],
    use_scm_version=True,
    setup_requires=[
        'setuptools_scm',
        'setuptools_scm_git_archive',
    ],
    zip_safe=False,
)
