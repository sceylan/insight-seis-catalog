# -*- coding:utf-8 -*-
from datetime import datetime
from .commontools import generate_object_id, to_datetime, to_float

class Arrival:
    """Class representing an arrival in the QuakeML data model."""
    def __init__(self, public_id=None, pick_id=None, time=None, phase_label=None, 
                 lower_uncertainty=None, upper_uncertainty=None):
        self.public_id = public_id
        self.pick_id = pick_id
        self.time = time
        self.phase_label = phase_label
        self.lower_uncertainty = lower_uncertainty
        self.upper_uncertainty = upper_uncertainty
    
        # Mars extension for single station pick
        self.single_station_pick: SingleStationPick = None

    def create_public_id(self, timestamp=None):
        """
        Generate a publicID for the Arrival object.
        Format: smi:insight.mqs/Arrival/YYYYMMDD-HHMMSS/unique_id
        This is used when Arrivals are created on the fly for new Arrival objects.
        """
        namespace = 'smi:insight.mqs'
        object_type = 'Arrival'
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        else:
            if not isinstance(timestamp, datetime):
                timestamp = to_datetime(timestamp)
            
        self.public_id = generate_object_id(namespace, object_type, timestamp)

    def set_single_station_pick(self, value):
        """ Set the single station extension for the arrival """
        if not isinstance(value, SingleStationPick):
            raise ValueError("Invalid SingleStationPick object")
        self.single_station_pick = value

    def get_single_station_pick(self):
        """ Get the single station extension for the arrival """
        return self.single_station_pick
    
    def get_frequency(self):
        """ Get the frequency from the single station extension """
        if self.single_station_pick:
            return self.single_station_pick.get_frequency()
        return None
    
    def get_freq_lower_uncertainty(self):
        """ Get the frequency lower uncertainty from the single station extension """
        if self.single_station_pick:
            return self.single_station_pick.get_freq_lower_uncertainty()
        return None
    
    def get_freq_upper_uncertainty(self):
        """ Get the frequency upper uncertainty from the single station extension """
        if self.single_station_pick:
            return self.single_station_pick.get_freq_upper_uncertainty()
        return None
    
    def set_pick_id(self, value):
        self.pick_id = value

    def get_pick_id(self):
        return self.pick_id
    
    def set_public_id(self, value):
        self.public_id = value

    def set_time(self, value):
        self.time = value

    def set_phase_label(self, value):
        self.phase_label = value

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
    
    def get_time(self):
        return self.time
    
    def get_phase_label(self):
        return self.phase_label
    
    def get_lower_uncertainty(self):
        if self.lower_uncertainty and not isinstance(self.lower_uncertainty, float):
            self.lower_uncertainty = float(self.lower_uncertainty)
        return self.lower_uncertainty
    
    def get_upper_uncertainty(self):
        if self.upper_uncertainty and not isinstance(self.upper_uncertainty, float):
            self.upper_uncertainty = float(self.upper_uncertainty)
        return self.upper_uncertainty
    
    def __repr__(self):
        return f'Arrival({self.public_id})'
    
    def __str__(self):
        _str = "Arrival: {:18s}".format(self.phase_label) + \
               f' Time: {self.time} +/-' + \
               f'[{self.lower_uncertainty}, {self.upper_uncertainty}]'
        
        if self.single_station_pick:
            _str += f'  {self.single_station_pick}'

        return _str
    
    def __eq__(self, other):
        if not isinstance(other, Arrival):
            return False
        
        return (self.time == other.time and
                self.phase_label == other.phase_label)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    

class Pick:
    """Class representing a pick in the QuakeML data model."""
    def __init__(self, public_id=None, time=None, phase_hint=None, 
                 lower_uncertainty=None, upper_uncertainty=None):
        self.public_id = public_id
        self.time = time
        self.phase_hint = phase_hint
        self.lower_uncertainty = lower_uncertainty
        self.upper_uncertainty = upper_uncertainty
    
        # Mars extension
        self.single_station_pick: SingleStationPick = None

    def set_single_station_pick(self, value):
        """ Set the single station extension for the pick """
        if not isinstance(value, SingleStationPick):
            raise ValueError("Invalid SingleStationPick object")
        self.single_station_pick = value

    def get_single_station_pick(self):
        """ Get the single station extension for the pick """
        return self.single_station_pick
    
    def create_public_id(self, timestamp=None):
        """
        Generate a publicID for the Pick object.
        Format: smi:insight.mqs/Pick/YYYYMMDD-HHMMSS/unique_id
        """
        namespace = 'smi:insight.mqs'
        object_type = 'Pick'
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        else:
            if not isinstance(timestamp, datetime):
                timestamp = to_datetime(timestamp)
            
        self.public_id = generate_object_id(namespace, object_type, timestamp)

    def set_public_id(self, value):
        self.public_id = value

    def set_time(self, value):
        self.time = value

    def set_phase_hint(self, value):
        self.phase_hint = value

    def set_lower_uncertainty(self, value):
        self.lower_uncertainty = value

    def set_upper_uncertainty(self, value):
        self.upper_uncertainty = value

    def get_public_id(self):
        return self.public_id
    
    def get_time(self):
        return self.time
    
    def get_phase_hint(self):
        return self.phase_hint
    
    def get_lower_uncertainty(self):
        return self.lower_uncertainty
    
    def get_upper_uncertainty(self):
        return self.upper_uncertainty
    
    def get_frequency(self):
        """ Get the frequency from the single station extension """
        if self.single_station_pick:
            return self.single_station_pick.get_frequency()
        return None
    
    def get_freq_lower_uncertainty(self):
        """ Get the frequency lower uncertainty from the single station extension """
        if self.single_station_pick:
            return self.single_station_pick.get_freq_lower_uncertainty()
        return None
    
    def get_freq_upper_uncertainty(self):
        """ Get the frequency upper uncertainty from the single station extension """
        if self.single_station_pick:
            return self.single_station_pick.get_freq_upper_uncertainty()
        return None
    
    def __repr__(self):
        return f'Pick({self.public_id})'
    
    def __str__(self):
        _str = "Pick: {:18s}".format(self.phase_hint) + \
               f' Time: {self.time} +/-' + \
               f'[{self.lower_uncertainty}, {self.upper_uncertainty}]'
        
        if self.single_station_pick:
            _str += f'  {self.single_station_pick}'

        return _str
    
    def __eq__(self, other):
        if not isinstance(other, Pick):
            return False
        
        return (self.time == other.time and
                self.phase_hint == other.phase_label)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    

class SingleStationPick():
    """Class representing a single station pick in the QuakeML data model Mars extension."""
    def __init__(self, public_id=None, frequency=None, pick_id=None,
                 freq_lower_uncertainty=None, freq_upper_uncertainty=None):
        self.public_id = public_id
        self.pick_id = pick_id
        self.frequency = frequency
        self.freq_lower_uncertainty = freq_lower_uncertainty
        self.freq_upper_uncertainty = freq_upper_uncertainty

    def set_public_id(self, value):
        self.public_id = value

    def set_frequency(self, value):
        self.frequency = to_float(value)

    def set_freq_lower_uncertainty(self, value):
        self.freq_lower_uncertainty = to_float(value)

    def set_freq_upper_uncertainty(self, value):
        self.freq_upper_uncertainty = to_float(value)

    def get_public_id(self):
        return self.public_id
    
    def get_frequency(self):
        return self.frequency
    
    def get_freq_lower_uncertainty(self):
        return self.freq_lower_uncertainty
    
    def get_freq_upper_uncertainty(self):
        return self.freq_upper_uncertainty
    
    def __repr__(self):
        return f'SingleStationPick({self.public_id})'
    
    def __str__(self):
        return f"SingleStationPick frequency: {self.frequency} +/-" + \
               f"[{self.freq_lower_uncertainty}, {self.freq_upper_uncertainty}]"
    
    def __eq__(self, other):
        if not isinstance(other, SingleStationPick):
            return False
        
        return (self.frequency == other.frequency)
    
    def __ne__(self, other):
        return not self.__eq__(other)