# -*- coding: utf-8 -*-

from setuptools import setup, find_packages

# Read version from the package
version = {}
with open("insightcatalog/version.py") as f:
    exec(f.read(), version)

setup(
    name='insightcatalog',
    version=version["__version__"],
    description='InSight Mars seismicity catalog management tools',
    author='Savas Ceylan, Fabian Euchner; ETH Zurich',
    author_email='savas.ceylan@eaps.ethz.com',
    packages=find_packages(),
    install_requires=[
        r.strip() for r in open("requirements.txt").readlines() if r.strip() and not r.startswith("#")
    ],
    python_requires='>=3.9',
)