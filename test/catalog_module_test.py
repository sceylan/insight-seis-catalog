#! /usr/bin/env python
# -*- coding: utf-8 -*-
import unittest

# Test imports
import insightcatalog as icat


catalog = icat.read_catalog('../insightcatalog/data/events_mars_extended_multiorigin_v14_2023-01-01.xml')
print(catalog)

for event in catalog:
    print(event)