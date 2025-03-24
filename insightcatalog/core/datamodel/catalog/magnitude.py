# -*- coding: utf-8 -*-
from datetime import datetime
from .commontools import generate_object_id, to_datetime

class Magnitude:
    """ Magnitude attributes."""
    def __init__(self, public_id=None, origin_id=None, magnitude_type=None, 
                 magnitude_value=None, lower_uncertainty=None, upper_uncertainty=None,
                 is_calculated=False):
        self.public_id = public_id
        self.origin_id = origin_id
        self.magnitude_type = magnitude_type
        self.magnitude_value = magnitude_value
        self.lower_uncertainty = lower_uncertainty
        self.upper_uncertainty = upper_uncertainty
        
        # If the magnitude is calculated on the fly, set is_calculated to True
        self.is_calculated = is_calculated

    def create_public_id(self, timestamp=None):
        """
        Generate a publicID for the Magnitude object.
        Format: smi:insight.mqs/Magnitude/YYYYMMDD-HHMMSS/unique_id
        This is used when magnitudes are calculated on the fly for new Magnitude
        objects.
        """
        namespace = 'smi:insight.mqs'
        object_type = 'Magnitude'
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        else:
            if not isinstance(timestamp, datetime):
                timestamp = to_datetime(timestamp)
            
        self.public_id = generate_object_id(namespace, object_type, timestamp)

    def set_is_calculated(self, value):
        """ Set the is_calculated attribute. True if the magnitude is calculated on the fly.
        If the Magnitude object is created from the catalog, this should be False.
        """
        self.is_calculated = value

    def get_is_calculated(self):
        """ Get the is_calculated attribute. """
        return self.is_calculated
    
    def set_origin_id(self, value):
        self.origin_id = value

    def get_origin_id(self):
        return self.origin_id   
    
    def set_public_id(self, value):
        self.public_id = value

    def set_type(self, value):
        self.magnitude_type = value

    def set_value(self, value):
        if value and not isinstance(value, float):
            value = float(value)
        self.magnitude_value = value

    def set_lower_uncertainty(self, value):
        if value and not isinstance(value, float):
            value = float(value)
        self.lower_uncertainty = value

    def set_upper_uncertainty(self, value):
        if value and not isinstance(value, float):
            value = float(value)
        self.upper_uncertainty = value

    def get_public_id(self):
        return self.public_id
    
    def get_type(self):
        return self.magnitude_type
    
    def get_value(self):
        if self.magnitude_value and not isinstance(self.magnitude_value, float):
            self.magnitude_value = float(self.magnitude_value)
        
        return self.magnitude_value
    
    def get_lower_uncertainty(self):
        if self.lower_uncertainty and not isinstance(self.lower_uncertainty, float):
            self.lower_uncertainty = float(self.lower_uncertainty)
        
        return self.lower_uncertainty
    
    def get_upper_uncertainty(self):
        if self.upper_uncertainty and not isinstance(self.upper_uncertainty, float):
            self.upper_uncertainty = float(self.upper_uncertainty)

        return self.upper_uncertainty
    
    def __repr__(self):
        return f'Magnitude({self.public_id})'
    
    def __str__(self):
        # return f'Magnitude: {self.public_id}, {self.magnitude_type}: {self.magnitude_value}'
        return f'Magnitude: {self.magnitude_type}: {self.magnitude_value}'
    
    def __eq__(self, other):
        if not isinstance(other, Magnitude):
            return False
        
        return (self.magnitude_type == other.magnitude_type and
                self.magnitude_value == other.magnitude_value)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    