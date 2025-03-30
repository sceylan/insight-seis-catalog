# -*- coding: utf-8 -*-
import json
import numpy as np
from insightcatalog.core.utils.customlogger import logger
from insightcatalog.core.utils.sorting import sort_events_by_distance


class Catalog:
    """ Class to store and manage a list of Events."""
    def __init__(self, events=None, source_file=None):
        self.events = events if events else []
        self.catalog_file = source_file

        # The results from the spectral fitting 
        self.spectral_fitting = None

        # Polarization analysis results
        self.polarization = None
        
    def __repr__(self):
        return f'Catalog({self.catalog_file})'
    
    def __str__(self):
        return f'Catalog file: {self.catalog_file}'
    
    def __len__(self):
        return len(self.events)
    
    def __getitem__(self, index):
        return self.events[index]
    
    def __iter__(self):
        return iter(self.events)
    
    def __contains__(self, event):
        return event in self.events
    
    def __add__(self, other):
        if not isinstance(other, Catalog):
            raise TypeError('Can only add Catalog to Catalog')
        return Catalog(self.events + other.events)
    

    @staticmethod
    def read(catalog_file):
        """ 
        Read the catalog from a QuakeML file. Same as calling the read_catalog() 
        method from the read module. It is provided here to that the Catalog 
        class has the same read() interface as the other classes in the datamodel 
        such as faults and annotated epochs.
        """
        # This import is done here instead of module header to avoid circular 
        # imports since this class is imported from the core.catalog.datamodel.read  
        # module as well. In case a module is placed in the module itself or one
        # directory above, handle the absolute path for complicated imports.
        try:
            from insightcatalog.core.quakeml_io import read_catalog
        except ImportError:
            from core.quakeml_io import read_catalog

        try:
            _catalog = read_catalog(catalog_file)
        except Exception as e:
            logger.error(f'Error reading catalog: {e}')
            raise e

        return _catalog
            
    def get_polarization(self):
        """ Return the polarization analysis results."""
        return self.polarization
    
    def get_spectral_fitting(self):
        """ Return the spectral analysis results."""
        return self.spectral_fitting
    
    def set_source_file(self, catalog_file):
        """ Set the source file for the catalog."""
        self.catalog_file = catalog_file

    def set_events(self, events):
        """ Set the events in the catalog."""
        self.events = events

    def append(self, event):
        """ Append an event to the catalog."""
        self.events.append(event)

    def extend(self, events):
        """ Extend the catalog with a list of events."""
        self.events.extend(events)

    def remove(self, event):
        """ Remove an event from the catalog."""
        self.events.remove(event)

    def clear(self):
        """ Clear the catalog."""
        self.events.clear()

    def get_event_by_name(self, event_name):
        """ Get an event by its name. Same oparation can also be done 
        by using the catalog.select(name=event_name) method. """
        for event in self.events:
            if event.get_event_name() == event_name:
                return event
        return None
    
    def get_list_of_events_by_name(self, event_names):
        """ Get a list of events by their names. """
        if isinstance(event_names, str):
            event_names = [event_names]
            
        events = []
        for event in self.events:
            if event.get_event_name() in event_names:
                events.append(event)
        return events
    

    def select(self, earth_event_types=None, mars_event_types=None, 
               min_magnitude=None, max_magnitude=None, quality=None, 
               name=None):
        """
        Filter the events based on the mars event type, earth event type, 
        min/max magnitudes, or event quality. Catalog is searched when the 
        name is given and other criteria are ignored. If name is None, then 
        the catalog is filtered based on the given criteria.
        """ 
        # If name is given, return the event with the given name.
        # Other criteria are not valid in this case since the caller
        # asked for a specific event.
        if name:
            return self.get_event_by_name(name)

        # If name is not given, then filter the events based on the given criteria.
        selected = []

        # Remove the letter Q from the quality list. The user might give the 
        # quality as 'QA', 'QB', etc. but the quality in the data model is stored
        # as 'A', 'B', etc.
        if quality:
            quality = [q.replace('Q', '') for q in quality]

        # Make sure the event types are lists
        if mars_event_types is None:
            mars_event_types = []
        elif isinstance(mars_event_types, str):
            mars_event_types = [mars_event_types]
        
        if earth_event_types is None:
            earth_event_types = []
        elif isinstance(earth_event_types, str):
            earth_event_types = [earth_event_types]

        # Loop through the events and select the ones that match 
        # the given criteria
        for event in self.events:
            if mars_event_types and \
                not event.get_mars_event_type() in mars_event_types:
                continue
            
            if earth_event_types and \
                not event.get_earth_event_type() in earth_event_types:
                continue

            if min_magnitude:
                if not event.get_preferred_magnitude() or \
                    event.get_preferred_magnitude().get_value() < min_magnitude:
                    continue

            if max_magnitude:
                if not event.get_preferred_magnitude() or \
                    event.get_preferred_magnitude().get_value() > max_magnitude:
                    continue

            if quality:
                if not event.get_quality() in quality:
                    continue

            selected.append(event)

        # Return a new catalog instance with the selected events
        return Catalog(selected)
    
    def sort_events(self, sort_by="distance", reverse=False):
        """ Sort the events in the catalog and return the sorted event names."""
        if sort_by == "distance":
            _names  = []
            _distances = []
            for event in self.events:
                _origin = event.get_preferred_origin()
                if _origin and _origin.get_distance():
                    _names.append(event.get_event_name())
                    _distances.append(_origin.get_distance())

            return sort_events_by_distance(_names, _distances)
        else:
            raise ValueError(f"Invalid sort_by value: {sort_by}")
    
    def breakdown(self, printout=True):
        """ Breakdown the catalog into a dictionary of event 
        qualitites and types in terms of the number of events."""
        breakdown = {}
        for event in self.events:
            _key_type = event.get_mars_event_type()
            if _key_type not in breakdown:
                breakdown[_key_type] = {}

            _key_quality = event.get_quality()
            if _key_quality not in breakdown[_key_type]:
                breakdown[_key_type][_key_quality] = 0

            breakdown[_key_type][_key_quality] += 1
        
        if printout:
            # Make a pretty print of the breakdown
            print('Catalog breakdown:')
            for _type, _qualities in breakdown.items():
                print(f'  {_type: <10} [{sum(_qualities.values())} events]')
                for _quality, _count in _qualities.items():
                    print(f'    |-- {_quality: <2}: {_count}')

        return breakdown
    
    def report(self):
        _source = self.catalog_file if self.catalog_file else 'Unknown'
        print(f'Catalog: {_source} [{len(self.events)} events')
        for event in self.events:
            event.report()
        print('----------------------')
        print(f'Catalog: {_source} [{len(self.events)} events]')
        print('--- End of catalog ---')
        