# -*- coding: utf-8 -*-
import numpy as np
from datetime import datetime
from .commontools import generate_object_id, to_datetime


class SingleStationParameters:
    """ Single-station distance and back-azimuth attributes."""
    def __init__(self):
        self.public_id = None
        self.sst_distance = None
        self.sst_baz = None
        self.sst_distance_variable = None
        self.sst_baz_variable = None
        self.sst_distance_pdf = None
        self.sst_baz_pdf = None

    def create_public_id(self, timestamp=None):
        """
        Generate a publicID for the SingleStationParameters object.
        Format: smi:insight.mqs/SingleStationParameters/YYYYMMDD-HHMMSS/unique_id
        This is used when SingleStationParameters are calculated on the fly for new SingleStationParameters
        objects.
        """
        namespace = 'smi:insight.mqs'
        object_type = 'SingleStationParameters'
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        else:
            if not isinstance(timestamp, datetime):
                timestamp = to_datetime(timestamp)
            
        self.public_id = generate_object_id(namespace, object_type, timestamp)

    def set_public_id(self, value):
        self.public_id = value

    def set_sst_distance(self, value):
        if value is not None:
            self.sst_distance = float(value)

    def set_sst_baz(self, value):
        if value is not None:
            self.sst_baz = float(value)

    def set_sst_distance_variable(self, value):
        if value is not None and isinstance(value, str):
            value = np.asarray(value.split(' ')).astype(float)
        self.sst_distance_variable = np.asarray(value)

    def set_sst_baz_variable(self, value):
        if value is not None and isinstance(value, str):
            value = np.asarray(value.split(' ')).astype(float)
        self.sst_baz_variable = np.asarray(value)

    def set_sst_distance_pdf(self, value):
        if value is not None and isinstance(value, str):
            value = np.asarray(value.split(' ')).astype(float)
        self.sst_distance_pdf = np.asarray(value)

    def set_sst_baz_pdf(self, value):
        if value is not None and isinstance(value, str):
            value = np.asarray(value.split(' ')).astype(float)
        self.sst_baz_pdf = np.asarray(value)

    def get_public_id(self):
        return self.public_id
    
    def get_sst_distance(self):
        if self.sst_distance and not isinstance(self.sst_distance, float):
            self.sst_distance = float(self.sst_distance)
        return self.sst_distance
    
    def get_sst_baz(self):
        if self.sst_baz and not isinstance(self.sst_baz, float):
            self.sst_baz = float(self.sst_baz)
        return self.sst_baz
    
    def get_sst_distance_variable(self):
        if self.sst_distance_variable is not None and isinstance(self.sst_distance_variable, str):
            self.sst_distance_variable = np.asarray(self.sst_distance_variable.split(' ')).astype(float)
        return self.sst_distance_variable
    
    def get_sst_baz_variable(self):
        if self.sst_baz_variable is not None and isinstance(self.sst_baz_variable, str):
            self.sst_baz_variable = np.asarray(self.sst_baz_variable.split(' ')).astype(float)
        return self.sst_baz_variable
    
    def get_sst_distance_pdf(self):
        if self.sst_distance_pdf is not None and isinstance(self.sst_distance_pdf, str):
            self.sst_distance_pdf = np.asarray(self.sst_distance_pdf.split(' ')).astype(float)
        return self.sst_distance_pdf
    
    def get_sst_baz_pdf(self):
        if self.sst_baz_pdf is not None and isinstance(self.sst_baz_pdf, str):
            self.sst_baz_pdf = np.asarray(self.sst_baz_pdf.split(' ')).astype(float)
        return self.sst_baz_pdf
    
    def __repr__(self):
        return f'SingleStationParameters({self.public_id})'
    
    def __str__(self):
        return f'SST :: Dist: {self.sst_distance} deg, Baz:  {self.sst_baz} deg'
    