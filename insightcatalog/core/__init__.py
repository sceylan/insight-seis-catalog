# -*- coding: utf-8 -*-
""" 
Exposes only the functional modules to the user. The data model 
classes should be imported from the submodules. 
"""
# Method for reading the catalog
from .quakeml_io import read_catalog

