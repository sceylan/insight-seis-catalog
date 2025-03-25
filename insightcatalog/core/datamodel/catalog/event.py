# -*- coding: utf-8 -*-
from typing import List, NamedTuple
import numpy as np
from .pickarrival import Pick
from .magnitude import Magnitude
from .origin import Origin
# from .waveform import Waveforms
from .spectradata import Spectrum, SpectrumContent, Spectra
from insightcatalog.core.utils.customlogger import logger
# from core.calculations.magnitude import calculate_magnitudes, calculate_amplitudes
# from core.calculations.spectra import calculate_spectra

class MarsEvent:
    """ Class to represent a Mars event. The class name is chosen 
    to avoid confusion with the obspy.Event class."""
    def __init__(self, public_id=None, mars_event_type=None, event_type=None, event_name=None):
        self.public_id = public_id
        self.mars_event_type = mars_event_type
        self.event_name = event_name
        self.event_type = event_type
        self.mars_event_type_interpretation = None

        # Origins
        self.origins: List[Origin] = []

        # Magnitudes
        self.magnitudes: List[Magnitude] = []

        # Picks
        self.picks: List[Pick] = []

        # Preferred origin and magnitude ids
        self.preferred_origin_id: str = None
        self.preferred_magnitude_id: str = None

        # The preferred origin
        self.preferred_origin: Origin = None

        # The preferred magnitude
        self.preferred_magnitude: Magnitude = None

        # The waveforms for all sensors. 
        self.waveforms: Waveforms = None

        # Amplitudes used for magnitude calculation
        self.amplitudes = {
            'A0': None, 'A0_err': None, 
            'tstar': None, 'tstar_err': None,
            'Z': {'Peak_MbP': None, 'Peak_MbS': None, 'Peak_M2.4': None},
            'N': {'Peak_MbP': None, 'Peak_MbS': None, 'Peak_M2.4': None},
            'E': {'Peak_MbP': None, 'Peak_MbS': None, 'Peak_M2.4': None}
            }
        
        # Amplitude metadata for the event for each of the components
        self.amplitude_metadata = {
            'Z': {'Peak_MbP': None, 'Peak_MbS': None, 'Peak_M2.4': None},
            'N': {'Peak_MbP': None, 'Peak_MbS': None, 'Peak_M2.4': None},
            'E': {'Peak_MbP': None, 'Peak_MbS': None, 'Peak_M2.4': None}
        }

        # Corner frequency and tstar for the event
        self.spectral_parameters = {
            'fc': None,
            'fc_low': None,
            'fc_high': None,
            'tstar': None,
            'tstar_low': None,
            'tstar_high': None,
            'manually_fitted': False
        }

        # Spectra for the event for different time windows
        self.vbb_spectra: Spectra = None
        self.sp_spectra: Spectra = None

        # Store the SDS path and inventory for the event for further use
        self.sds_path: str = None
        self.inventory: str = None

    def set_mars_event_type_interpretation(self, value):
        self.mars_event_type_interpretation = value

    def get_mars_event_type_interpretation(self):
        return self.mars_event_type_interpretation
    
    def check_magnitudes_against_arrivals(self):
        """ Check if the magnitudes are consistent with the arrivals. """
        required_magnitudes = {
            'P': 'mb_P', 'S': 'mb_S', 'Peak_2.4': 'm2.4'
        }

        for arrival in self.get_preferred_origin().get_arrivals():
            for key, value in required_magnitudes.items():
                if arrival.get_phase_label() == key:
                    if not self.get_magnitude(value):
                        logger.warning(f'Magnitude {value} is missing for the event')

        
    def set_spectral_parameters(self, **kwargs):
        """
        Set or update the spectral parameters for the event without overwriting
        pre-assigned values.

        Parameters:
            kwargs: Key-value pairs of spectral parameters to update. Valid keys are:
                - 'fc': Corner frequency
                - 'fc_low': Lower bound of corner frequency
                - 'fc_high': Upper bound of corner frequency
                - 'tstar': Attenuation parameter
                - 'tstar_low': Lower bound of t-star
                - 'tstar_high': Upper bound of t-star
                - 'manully_fitted': Boolean flag to indicate if the spectral parameters are manually fitted

        Example:
            event.set_spectral_parameters(fc=2.5, tstar=0.03)
        """
        # Allowed keys in the spectral parameters
        allowed_keys = {'fc', 'fc_low', 'fc_high', 'tstar', 'tstar_low', 'tstar_high', 'manually_fitted'}

        for key, value in kwargs.items():
            if key not in allowed_keys:
                raise ValueError(f"Invalid parameter '{key}'. Allowed parameters are: {allowed_keys}")
            self.spectral_parameters[key] = value

    def set_spectral_fit_as_manual(self):
        """ Set the flag to indicate if the spectral fit is manually fitted."""
        self.spectral_parameters['manually_fitted'] = True

    def set_spectral_fit_as_automatic(self):
        """ Set the flag to indicate if the spectral fit is automatically calculated."""
        self.spectral_parameters['manually_fitted'] = False

    def is_spectral_fit_manual(self):
        return self.spectral_parameters.get('manully_fitted', False)
    
    def get_fc(self):
        """Get the corner frequency (fc)."""
        return self.spectral_parameters.get('fc', None)

    def get_fc_low(self):
        """Get the lower bound of the corner frequency."""
        return self.spectral_parameters.get('fc_low', None)

    def get_fc_high(self):
        """Get the upper bound of the corner frequency."""
        return self.spectral_parameters.get('fc_high', None)

    def get_tstar(self):
        """Get the attenuation parameter (t-star)."""
        return self.spectral_parameters.get('tstar', None)

    def get_tstar_low(self):
        """Get the lower bound of the attenuation parameter."""
        return self.spectral_parameters.get('tstar_low', None)

    def get_tstar_high(self):
        """Get the upper bound of the attenuation parameter."""
        return self.spectral_parameters.get('tstar_high', None)

    def set_sds_path(self, sds_path):
        """ Set the SDS path for reading waveforms. """
        self.sds_path = sds_path

    def get_sds_path(self):
        """ Get the SDS path used for reading waveforms. """
        return self.sds_path
    
    def set_inventory(self, inventory):
        self.inventory = inventory

    def get_inventory(self):
        return self.inventory

    def is_meteorite_impact(self):
        return self.event_type == 'meteorite'
    
    def is_thermal_event(self):
        """ Check if the event is a thermal event (SF events)"""
        return self.get_event_name().startswith('T')
    
    def is_deep_learning_event(self):
        """ Check if the event is created by deep learning analysis."""
        return self.get_event_name().startswith('D')
    
    def set_spectrum(self, amplitude, frequency, instrument, time_window, component):
        """ Set the spectrum for the event. """
        # select the correct spectra object based on the instrument
        if instrument == 'VBB':
            # Initialize the spectra if not already done
            if self.vbb_spectra is None:
                empty_spectrum = Spectrum(
                    Z=SpectrumContent(None, None),
                    N=SpectrumContent(None, None),
                    E=SpectrumContent(None, None)
                )
                self.vbb_spectra = Spectra(
                    all=empty_spectrum._replace(), 
                    noise=empty_spectrum._replace(), 
                    P=empty_spectrum._replace(), 
                    S=empty_spectrum._replace())

            if time_window not in self.vbb_spectra._fields:
                raise ValueError('Invalid time window')

            if component not in ['Z', 'N', 'E']:
                raise ValueError('Invalid component')

            spectrum_content = SpectrumContent(frequency, amplitude)
            current_spectrum = getattr(self.vbb_spectra, time_window)
            updated_spectrum = current_spectrum._replace(**{component: spectrum_content})
            self.vbb_spectra = self.vbb_spectra._replace(**{time_window: updated_spectrum})
        
        elif instrument == 'SP':
            # Initialize the spectra if not already done
            if self.sp_spectra is None:
                empty_spectrum = Spectrum(
                    Z=SpectrumContent(None, None),
                    N=SpectrumContent(None, None),
                    E=SpectrumContent(None, None)
                )
                self.sp_spectra = Spectra(
                    all=empty_spectrum._replace(), 
                    noise=empty_spectrum._replace(), 
                    P=empty_spectrum._replace(), 
                    S=empty_spectrum._replace())

            if time_window not in self.sp_spectra._fields:
                raise ValueError('Invalid time window')

            if component not in ['Z', 'N', 'E']:
                raise ValueError('Invalid component')

            spectrum_content = SpectrumContent(frequency, amplitude)
            current_spectrum = getattr(self.sp_spectra, time_window)
            updated_spectrum = current_spectrum._replace(**{component: spectrum_content})
            self.sp_spectra = self.sp_spectra._replace(**{time_window: updated_spectrum})

           
    def get_spectra(self, instrument, time_window=None):
        """ Get the spectra for the time window. 
        Time window can be 'all', 'noise', 'P', or 'S'. Instrument can be 
        'VBB' or 'SP'."""
        if instrument not in ['VBB', 'SP']:
            raise ValueError('Invalid instrument. Use "VBB" or "SP" for the spectra.')
        
        if time_window is not None and time_window not in ['all', 'noise', 'P', 'S']:
            raise ValueError('Invalid time window. Use "all", "noise", "P", or "S" for the spectra.')

        if instrument == 'VBB' and self.vbb_spectra is None:
            return None
        elif instrument == 'SP' and self.sp_spectra is None:
            return None
        
        if time_window is None:
            # Return all spectra
            if instrument == 'VBB':
                return self.vbb_spectra
            elif instrument == 'SP':
                return self.sp_spectra
        else:
            # Return the spectra for the specified time window
            if instrument == 'VBB':
                if time_window not in self.vbb_spectra._fields:
                    raise ValueError('Invalid time window')
                return getattr(self.vbb_spectra, time_window)
            elif instrument == 'SP':
                if time_window not in self.sp_spectra._fields:
                    raise ValueError('Invalid time window')
                return getattr(self.sp_spectra, time_window)
    
    def get_amplitudes(self):
        """ Return all amplitudes as a dictionary"""
        return self.amplitudes
    
    def set_amplitudes(self, amplitudes):
        """ Set the amplitudes for the event. The amplitudes should be a 
        dictionary with keys 'P', 'S', and '24' for phases per component,
        and A0, A0_err for spectral amplitude per event."""
        # Make sure first order keys are components
        for key in amplitudes.keys():
            if key not in ['Z', 'N', 'E', 'A0', 'A0_err']:
                raise ValueError('Invalid component "{key}" in the amplitudes dictionary')
            
            # Make sure second order keys are valid amplitude keys
            _amp_dict = amplitudes[key]

            for _key in _amp_dict.keys():
                if _key not in self.amplitudes.keys():
                    raise ValueError('Invalid amplitude key "{_key}" for component "{key}"')
            
        self.amplitudes = amplitudes

    def _correct_amplitude_key(self, key):
        """Convert the amplitude key to the standard format for some common alternatives."""
        if key in ['24', '24Hz', '2.4Hz', '24hz', '2.4hz']:
            key = '2.4'
        elif key in ['p']:
            key = 'P'
        elif key in ['s']:
            key = 'S'
        elif key in ['a0', 'A0', 'MFB', 'mfb']:
            key = 'A0'
        return key

    def get_amplitude(self, component, key):
        """Get the amplitude for the specified key. 
        The key can be 'P', 'S', 'A0' or '2.4'."""
        # Check for possible alternative amplitude keys and convert them 
        key = self._correct_amplitude_key(key)
        return self.amplitudes[component][key]
    
    def set_amplitude(self, key, value):
        """Set the amplitude for the specified key. The key can be 'P', 'S', 'A0' or '2.4'."""
        # Convert the key to the standard format for some common alternatives
        key = self._correct_amplitude_key(key)
        self.amplitudes[key] = value

    def append_pick(self, pick):
        if not isinstance(pick, Pick):
            raise ValueError('Invalid "Pick" object')
        self.picks.append(pick)

    def get_waveforms(self):
        return self.waveforms
    
    def set_picks(self, picks):
        self.picks = picks

    def get_picks(self):
        return self.picks
    
    def get_pick(self, label):
        """Return the pick object for the specified label. 
        If the pick is not found, return None."""
        for pick in self.picks:
            if pick.get_phase_label() == label:
                return pick
        return None
    
    def append_magnitude(self, magnitude):
        self.magnitudes.append(magnitude)

    def set_magnitudes(self, magnitudes):
        self.magnitudes = magnitudes

    def get_magnitudes(self):
        """ Return the magnitudes for the event. If no magnitudes are set,
        return None."""
        if len(self.magnitudes) == 0:
            return None
        return self.magnitudes
    
    def clear_magnitudes(self):
        """Remove all magnitudes from the event. This might be useful
        when magnitudes are recalculated for a clean start."""
        self.magnitudes.clear()

    # def calculate_magnitudes(self, spectral_fitting=None, winlen_sec=25, padding=True, detick_nfsamp=0):
    #     """
    #     Calculates the magnitudes for the event. The magnitudes are calculated based 
    #     on the picks and arrivals in the event. If the event is analyzed via the 
    #     spectral fitting, the moment magnitude is calculated using the A0 from manual 
    #     spectral fitting. Otherwise, spectral fitting is performed on the event to obtain A0.
    #     """
    #     logger.info('Calculating new magnitudes for the event')

    #     # Check if the preferred origin is set
    #     if self.get_preferred_origin() is None and len(self.origins) == 0:
    #         logger.error('No origins for the event. Cannot calculate magnitudes.')
    #         return

    #     origin = self.get_preferred_origin() or self.origins[0]
    #     if len(origin.get_arrivals()) == 0:
    #         logger.error('No arrivals are set for the (preferred) origin')
    #         return

    #     # Calculate the amplitudes for the event
    #     calculate_amplitudes(event=self, spectral_fitting=spectral_fitting,
    #                          winlen_sec=winlen_sec, padding=padding, 
    #                          detick_nfsamp=detick_nfsamp)

    #     # Calculate the magnitudes for the event
    #     calculate_magnitudes(event=self)
        
    def set_preferred_origin_public_id(self, public_id):
        self.preferred_origin_id = public_id

    def get_preferred_origin_public_id(self):
        return self.preferred_origin_id
    
    def set_preferred_magnitude_public_id(self, public_id):
        self.preferred_magnitude_id = public_id

    def get_preferred_magnitude_public_id(self):
        return self.preferred_magnitude_id
    
    def set_preferred_magnitude(self, magnitude):
        if not isinstance(magnitude, Magnitude):
            raise ValueError('Invalid magnitude type')
        self.preferred_magnitude = magnitude

    def get_preferred_magnitude(self):
        # If the preferred magnitude is not set, determine it from the list of
        # existing magnitudes so that we don't have to loop every time
        if self.preferred_magnitude is None:
            for magnitude in self.magnitudes:
                if magnitude.get_public_id() == self.preferred_magnitude_id:
                    self.preferred_magnitude = magnitude
                    break

        return self.preferred_magnitude
    
    def set_preferred_origin(self, origin):
        if not isinstance(origin, Origin):
            raise ValueError('Invalid origin type')
        self.preferred_origin = origin

    def get_preferred_origin(self):
        # If the preferred origin is not set, determine it from the list
        # of existing origins so that we don't have to loop every time
        if self.preferred_origin is None:
            for origin in self.origins:
                if origin.get_public_id() == self.preferred_origin_id:
                    self.preferred_origin = origin
                    break

        return self.preferred_origin
    
    def get_quality(self):
        """Shorthand for getting the quality of the preferred origin."""
        return self.get_preferred_origin().get_quality()
    
    def set_origins(self, origins):
        self.origins = origins

    def get_origins(self):
        return self.origins
    
    def set_public_id(self, value):
        self.public_id = value

    def get_public_id(self):
        return self.public_id
    
    def set_mars_event_type(self, value):
        self.mars_event_type = value

    def get_mars_event_type(self):
        return self.mars_event_type
    
    def set_event_name(self, value):
        self.event_name = value

    def get_event_name(self):
        """Same as get_name(). For avoiding confusion and 
        interruptions while coding"""
        return self.event_name
    
    def get_name(self):
        """ Same as get_event_name(). """
        return self.event_name
    
    def set_earth_event_type(self, value):
        self.event_type = value

    def get_earth_event_type(self):
        return self.event_type
    
    def __repr__(self):
        return f'Event({self.public_id})'
    
    def __str__(self):
        # Format the string to have a fixed width for the event name and type
        _str = "{:8s}{:8s}{}".format(
            self.event_name, 
            self.get_mars_event_type() + ", Q" + self.get_quality(), 
            self.public_id)
        return _str
    
    def __eq__(self, other):
        if not isinstance(other, MarsEvent):
            return False
        
        return (self.event_name == other.event_name)
    
    def __ne__(self, other):
        return not self.__eq__(other)
    
    def __iter__(self):
        return iter(self.origins)
    
    def __len__(self):
        return len(self.origins)
    
    def __getitem__(self, index):
        return self.origins[index]
    
    def __contains__(self, origin):
        return origin in self.origins

    def append_origin(self, origin):
        if not isinstance(origin, Origin):
            raise ValueError('Invalid origin type')
        self.origins.append(origin)

    def remove_origin(self, origin):
        self.origins.remove(origin)

    def clear_origins(self):
        self.origins.clear()

    def get_number_of_origins(self):
        return len(self.origins)
    
    def get_pick_for_arrival(self, arrival):
        """Return the pick object for the specified arrival. 
        If the arrival is not found, return None."""
        for pick in self.picks:
            if pick.get_public_id() == arrival.get_pick_id():
                return pick
        return None
    
    # def read_waveforms(self, sds_path=None, inventory=None, output=['DISP'], 
    #                    instruments=['VBB'], rotate_to_zne=False, save_local=False,
    #                    channels_and_locs=None):
    #     """ Read the waveforms for the event. If the waveforms are already
    #     read, this method will overwrite the previous object."""
    #     # Try with the internally stored path and inventory, if not provided.
    #     # Hopefully, the event has been read before and these are already set.
    #     if sds_path is None:
    #         sds_path = self.sds_path
    #     if inventory is None:
    #         inventory = self.inventory

    #     # Check again if the path and inventory are set
    #     if sds_path is None or inventory is None:
    #         logger.error('No SDS path or inventory is set for the event')
    #         raise ValueError('No SDS path or inventory is set for the event')
        
    #     # Initialize the waveforms object, which stores all the waveforms
    #     # for the event, whether seismic or not.
    #     self.waveforms = Waveforms(
    #         sds_path=sds_path, inventory=inventory, event=self)
        

    #     # Find out the earliest and latest arrival times for the event
    #     preferred_origin = self.get_preferred_origin()
    #     arrival_times = [
    #         arrival.get_time() for arrival in preferred_origin.get_arrivals()
    #             if arrival.get_time() is not None
    # ]
    #     origin_time = self.get_preferred_origin().get_origin_time()
    #     arrival_times.append(origin_time)
        
    #     # Calculate the buffer
    #     if not arrival_times:
    #         logger.warning('No valid arrival or origin times found for the event')
    #         buffer = (300, 300)  # Default buffer
    #     else:
    #         earliest_time = min(arrival_times)  # Earliest of all times
    #         buffer_before = int(float(origin_time) - float(earliest_time)) + 300
    #         buffer_after = 300
    #         buffer = (buffer_before, buffer_after)
            
    #     # Read the waveforms
    #     self.waveforms.read_waveforms(output=output, instruments=instruments,
    #                                   time_buffer=buffer,
    #                                   save_local=save_local, rotate_to_zne=rotate_to_zne,
    #                                   channels_and_locs=channels_and_locs)

    #     # Keep the inventory and path for further use
    #     self.inventory = inventory
    #     self.sds_path = sds_path

    def report(self, include_magnitudes=True, include_picks=False, 
               include_arrivals=True, include_origins=False):
        print(f'Event: {self.event_name} [{self.public_id}]')
        print(f'\tMars event type: {self.get_mars_event_type()}')
        print(f'\tMars event type interpretation: {self.get_mars_event_type_interpretation()}')
        print(f'\tEarth event type: {self.get_earth_event_type()}') 
        print(f"\tNumber of origins: {len(self.origins)}")
        
        if include_origins:
            print('\tOrigins:')
            for origin in self.origins:
                print('\t- '+ str(origin))
        
        if self.get_preferred_origin() is None:
            print('\tPreferred origin: None')
        else:
            print('\tPreferred Origin:')
            print('\t- ' + str(self.get_preferred_origin()))
        
        
        if self.get_preferred_magnitude() is None:
            print('\tPreferred Magnitude: None')
        else:
            print('\tPreferred Magnitude:')
            print('\t- ' + str(self.get_preferred_magnitude()))

        if include_magnitudes:
            print('\tMagnitudes:')
            for magnitude in self.magnitudes:
                print('\t├─ ' + str(magnitude))
        
        if include_picks and self.picks:
            print('\tPicks:')
            for pick in self.picks:
                print('\t├─ ' + str(pick))
        
        if include_arrivals and self.get_preferred_origin() is not None:
            print('\tArrivals (preferred origin):')
            for arrival in self.get_preferred_origin().get_arrivals():
                print('\t├─ ' + str(arrival))
        print('---')
        

    def plot_uncertainties(self, method, threshold_for_pdf, sigma_for_cdf, show=True, outfile=None):
        """ 
        Plot the distance and backazimuth uncertainties for a single event. 
        This method is a wrapper around the plot_uncertainty method in the
        origin object. 
        """
        if self.get_preferred_origin() is None and self.origins[0] is None:
            logger.error('No preferred origin is set for the event')
            return

        # Call the plot function from the eventbased uncertainty module
        # via the origin object
        origin = self.get_preferred_origin() or self.origins[0]
        origin.plot_uncertainties(method, threshold_for_pdf, sigma_for_cdf, show, outfile)