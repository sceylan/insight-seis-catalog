# -*- coding: utf-8 -*-
from datetime import datetime
from typing import List
from .pickarrival import Arrival
from .magnitude import Magnitude
from insightcatalog.core.utils.customlogger import logger
from .singlestation import SingleStationParameters
from .commontools import generate_object_id, to_datetime

class Origin:
    """The representation of an Origin in the QuakeML data model."""
    def __init__(self, public_id=None, origin_time=None, latitude=None, longitude=None, 
                 depth=None, distance=None, baz=None, quality=None, snr=None):
        self.public_id = public_id
        self.origin_time = origin_time
        self.latitude = latitude
        self.longitude = longitude
        self.depth = depth
        self.distance = distance
        self.baz = baz
        self.quality = quality
        self.snr = snr

        # Single station parameters
        self.sst_parameters: SingleStationParameters = None

        # Magnitudes
        self.magnitudes: List[Magnitude] = []

        # Arrivals
        self.arrivals: List[Arrival] = []

        # Parent event for cross-referencing. Not a part of the QuakeML data model.
        self.parent_event = None

        # Source of the origin: GUI or DL. This is not a part of the QuakeML data model.
        self.source = None

    def create_public_id(self, timestamp=None):
        """
        Generate a publicID for the Origin object.
        Format: smi:insight.mqs/Origin/YYYYMMDD-HHMMSS/unique_id
        """
        namespace = 'smi:insight.mqs'
        object_type = 'Origin'
        
        if timestamp is None:
            timestamp = datetime.now().strftime('%Y%m%d-%H%M%S')
        else:
            if not isinstance(timestamp, datetime):
                timestamp = to_datetime(timestamp)
            
        self.public_id = generate_object_id(namespace, object_type, timestamp)

    def set_as_gui_origin(self):
        """ Set the origin as a GUI origin. """
        self.source = 'GUI'
    
    def set_as_dl_origin(self):
        """ Set the origin as a DL origin. """
        self.source = 'DL'

    def set_origin_type(self, origin_type):
        """ Set the origin type. """
        self.source = origin_type

    def is_gui_origin(self):
        """ Check if the origin is a GUI origin. """
        return self.source == 'GUI'
    
    def is_dl_origin(self):
        """ Check if the origin is a DL origin. """
        return self.source == 'DL'
    
    def set_parent_event(self, parent_event):
        self.parent_event = parent_event

    def get_parent_event(self):
        return self.parent_event
    
    def append_arrival(self, arrival):
        if not isinstance(arrival, Arrival):
            raise ValueError('Invalid "Arrival" object')
        self.arrivals.append(arrival)

    def set_arrivals(self, arrivals):
        self.arrivals = arrivals

    def get_arrivals(self):
        return self.arrivals
    
    def get_arrival(self, phase_label):
        for arrival in self.arrivals:
            if arrival.get_phase_label() == phase_label:
                return arrival
        return None
    
    def set_sst_parameters(self, sst_parameters: SingleStationParameters):
        self.sst_parameters = sst_parameters

    def get_sst_parameters(self): 
        return self.sst_parameters
    
    def append_magnitude(self, magnitude):
        self.magnitudes.append(magnitude)

    def set_magnitudes(self, magnitudes):
        self.magnitudes = magnitudes

    def get_magnitudes(self):
        return self.magnitudes
    
    def set_public_id(self, value):
        self.public_id = value

    def set_origin_time(self, value):
        self.origin_time = value

    def set_latitude(self, value):
        self.latitude = value

    def set_longitude(self, value):
        self.longitude = value

    def set_depth(self, value):
        self.depth = value

    def set_distance(self, value):
        # Set the distance in the SST parameters as well
        self.distance = value
        
        if self.sst_parameters is not None:
            self.sst_parameters.set_sst_distance(value)
        else:
            new_sst = SingleStationParameters()
            new_sst.set_sst_distance(value)
            self.set_sst_parameters(new_sst)

    def set_baz(self, value):
        self.baz = value
        
    def set_quality(self, value):
        self.quality = value

    def set_snr(self, value):
        self.snr = value

    def get_public_id(self):
        return self.public_id
    
    def get_origin_time(self):
        return self.origin_time
    
    def get_latitude(self):
        if self.latitude and not isinstance(self.latitude, float):
            self.latitude = float(self.latitude)
        return self.latitude
    
    def get_longitude(self):
        if self.longitude and not isinstance(self.longitude, float):
            self.longitude = float(self.longitude)
        return self.longitude
    
    def get_depth(self):
        if self.depth and not isinstance(self.depth, float):
            self.depth = float(self.depth)
        return self.depth
    
    def get_distance(self):
        if self.distance and not isinstance(self.distance, float):
            self.distance = float(self.distance)
        
        return self.sst_parameters.get_sst_distance() or self.distance
    
    def get_distance_pdf(self):
        """ Shorthand method to get the distance PDF from the SST parameters."""
        return self.sst_parameters.get_sst_distance_pdf()
    
    def set_distance_pdf(self, value):
        self.sst_parameters.set_sst_distance_pdf(value)

    def get_distance_variable(self):
        return self.sst_parameters.get_sst_distance_variable()
    
    def set_distance_variable(self, value):
        self.sst_parameters.set_sst_distance_variable(value)

    def get_baz(self):
        if self.baz and not isinstance(self.baz, float):
            self.baz = float(self.baz)
        return self.baz
    
    def get_baz_pdf(self):
        """ Shorthand method to get the backazimuth PDF from the SST parameters."""
        return self.sst_parameters.get_sst_baz_pdf()
    
    def set_baz_pdf(self, value):
        self.sst_parameters.set_sst_baz_pdf(value)

    def get_baz_variable(self):
        return self.sst_parameters.get_sst_baz_variable()
    
    def set_baz_variable(self, value):
        self.sst_parameters.set_sst_baz_variable(value)

    def get_quality(self):
        return self.quality
    
    def get_snr(self):
        if self.snr and not isinstance(self.snr, float):
            self.snr = float(self.snr)
        return self.snr
    
    def calculate_uncertainty(self, variable, method, threshold=0.25, sigma=1):
        """ Triggers the calculation of the distance uncertainty method 
        with the PDF stored in the class object. 
        
        Parameters:
        variable: str
            The variable to calculate the uncertainty for, either 
            'distance', 'dist', 'baz' or 'backazimuth'. Required. 
        method: str
            The method to use for the uncertainty calculation, 
            either 'pdf' or 'cdf'. Required.
        threshold: float
            The percentage of the maximum probability that will be subtracted 
            from the PDF to calculate the uncertainty. Used only for the 'pdf' method.
        sigma: int
            The standard deviation to use for the CDF calculation. Used only 
            for the 'cdf' method.
        """
        # Get the SST parameters
        single_sta = self.get_sst_parameters()

        # Check if the SST parameters are available
        if single_sta is None:
            logger.error('Cannot calculate uncertainty. SST parameters are None.')
            return None
        
        # Get the variable and the PDF for the uncertainty calculation
        # depending on the 'variable' parameter
        if variable in ['dist', 'distance']:
            _variable = single_sta.get_sst_distance_variable()
            _pdf = single_sta.get_sst_distance_pdf()
        elif variable in ['baz', 'backazimuth']:
            _variable = single_sta.get_sst_baz_variable()
            _pdf = single_sta.get_sst_baz_pdf()
        else:
            logger.error(f'Invalid variable for uncertainty calculation: {variable}')
            raise ValueError(f'Invalid variable for uncertainty calculation: {variable}')

        if _variable is None or _pdf is None:
            logger.error(f'Cannot calculate uncertainty. Variable or PDF is None.')
            return None
        
        # Calculate the uncertainty depending on the method parameter
        if method == 'pdf':
            # Calculate the PDF uncertainty. The threshold is the percentage of the 
            # maximum probability that will be subtracted from the PDF to calculate 
            # the uncertainty.
            roots, wrap_around, max_prob_x = pdf_uncertainty(_variable, _pdf, threshold=threshold)
        elif method == 'cdf':
            # Calculate the CDF uncertainty. sigma is the standard deviation, e.g. 1, 2, 3
            roots, wrap_around, max_prob_x = cdf_uncertainty(_variable, _pdf, sigma=sigma)
        else:
            # Invalid method
            logger.error(f'Invalid method for distance uncertainty calculation: {method}')
            raise ValueError(f'Invalid method for distance uncertainty calculation: {method}')
        
        return roots, wrap_around, max_prob_x

    def plot_uncertainties(self, method, threshold_for_pdf=0.25, sigma_for_cdf=1, show=True, outfile=None, **kwargs):
        """ Triggers the plotting of the distance uncertainty method 
        with the PDF stored in the class object. 
        
        Parameters:
        method: str
            The method to use for the uncertainty calculation, 
            either 'pdf' or 'cdf'. Required.
        threshold_for_pdf: float
            The percentage of the maximum probability that will be subtracted 
            from the PDF to calculate the uncertainty. Used only for the 'pdf' method.
        sigma_for_cdf: int
            The standard deviation to use for the CDF calculation. Used only 
            for the 'cdf' method.
        """
        import warnings
        warnings.warn("Not implemented yet", DeprecationWarning)
        return
    
        # Call the plot function from the eventbased uncertainty module
        # with this origin object, method, threshold and sigma
        if not method in ['pdf', 'cdf']:
            logger.error(f'Invalid method for uncertainty plot: {method}')
            raise ValueError(f'Invalid method for uncertainty plot: {method}')
        
        # uncertainty_plot(self, method=method, threshold_for_pdf=threshold_for_pdf, 
        #                  sigma_for_cdf=sigma_for_cdf, show=show, outfile=outfile, 
        #                  **kwargs)

    def __repr__(self):
        return f'Origin({self.public_id})'
    
    def __str__(self):
        _str = f'Origin: {self.public_id}, Quality: {self.quality}\n'
        _str += f'\t  O.Time: {self.origin_time}, Lat/Lon: {self.latitude}, {self.longitude}, Depth: {self.depth}\n'
        _str += f'\t  BED :: Dist: {self.distance} deg, Baz: {self.baz} deg \n'
        _str += '\t  ' + str(self.sst_parameters)
        return _str
    
    def __eq__(self, other):
        if not isinstance(other, Origin):
            return False
        
        return (self.origin_time == other.origin_time and
                self.latitude == other.latitude and
                self.longitude == other.longitude and
                self.depth == other.depth)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    