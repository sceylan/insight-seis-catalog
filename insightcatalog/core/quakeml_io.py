# -*- coding:utf-8 -*-
"""Parser method for the catalog"""
import time
import xmltodict
from obspy import UTCDateTime
from .utils.customlogger import logger
from .datamodel.catalog import (Origin, Catalog, Magnitude, MarsEvent, 
                                SingleStationParameters, Arrival, Pick,
                                SingleStationPick)

# Keys for the location quality
_QUALITY_KEYS = {
    'MarsLocationQualityType#D': 'D',
    'MarsLocationQualityType#C': 'C',
    'MarsLocationQualityType#B': 'B',
    'MarsLocationQualityType#A': 'A'
}

# Keys for mapping the event types
_EVENT_TYPE_KEYS = {
    'MarsEventType#BROADBAND': 'BB',
    'MarsEventType#WIDEBAND': 'WB',
    'MarsEventType#LOW_FREQUENCY': 'LF',
    'MarsEventType#VERY_HIGH_FREQUENCY': 'VF',
    'MarsEventType#HIGH_FREQUENCY': 'HF',
    'MarsEventType#2.4_HZ': '24',
    'MarsEventType#SUPER_HIGH_FREQUENCY': 'SF',
    # Deep learning event types
    'MarsEventType#DL-HIGH_FREQUENCY': 'DL-HF',
    'MarsEventType#DL-VERY_HIGH_FREQUENCY': 'DL-VF',
    'MarsEventType#DL-LOW_FREQUENCY': 'DL-LF',
    'MarsEventType#DL-BROADBAND': 'DL-BB',
    'MarsEventType#DL-WIDEBAND': 'DL-WB',
    'MarsEventType#DL-2.4_HZ': 'DL-24',
    'MarsEventType#DL-SUPER_HIGH_FREQUENCY': 'DL-SF'
}

# Keys for the event interpretation
_EVENT_INTERPRETATION_KEYS = {
    "MarsEventTypeInterpretation#SWARM": "swarm",
    "MarsEventTypeInterpretation#IMPACT": "impact",
    "MarsEventTypeInterpretation#TECTONIC": "tectonic",
    "MarsEventTypeInterpretation#UNKNOWN": "unknown"
}


def _parse_event_interpretation(event_interpretation):
    """Parse the event interpretation"""
    if event_interpretation is None:
        return None
    
    for key, value in _EVENT_INTERPRETATION_KEYS.items():
        if key in event_interpretation:
            return value
    return None

def _parse_event_name(description):
    """Parse the event from event description block."""
    event_name = None
    
    for _desc in description:
        # Check if the description is a dictionary. This means the event
        # is full marsquake processed in the MQS GUI
        if isinstance(_desc, dict):
            if _desc['type'] == 'earthquake name':
                event_name = _desc['text']

        # If the description is a string, then the event is added to the
        # catalog afterwards. This is the case for auto-processed thermal 
        # events named as T0001, for instance.
        elif isinstance(_desc, str):
            if description['type'] == 'earthquake name':
                event_name = description['text']
            else:
                raise ValueError('Invalid description:\n' + description)
            
    return event_name

def _parse_quality(quality):
    """
    Return a string for the location quality depending on the given SMI.
    """
    if quality is None:
        return None
    
    for key, value in _QUALITY_KEYS.items():
        if key in quality:
            return value
    return None

def _parse_event_type(event_type):
    """Parse the event type"""
    if event_type is None:
        return None
    
    for key, value in _EVENT_TYPE_KEYS.items():
        if key in event_type:
            return value
    return None
    
def _parse_origin(origin):
    """Parse the origin information"""
    if not isinstance(origin, dict):
        raise ValueError('Invalid origin type')
    
    # Get the origin id and time
    origin_id = origin['@publicID']
    origin_time = UTCDateTime(origin['time']['value'])
            
    # Get the latitude, longitude
    latitude = origin['latitude']['value']
    longitude = origin['longitude']['value']

    # Unless the depth is in the catalog, the default is 50 km.
    # Units are in meters
    depth = 50 * 1000.0
    if 'depth' in origin:
        depth = origin['depth']['value']
            
    # The location quality
    quality = None
    if 'mars:locationQuality' in origin:
        quality = origin['mars:locationQuality']
            
    # Distance
    mars_distance = None
    if 'mars:distance' in origin:
        mars_distance = origin['mars:distance']['mars:value']
            
    # Backazimuth
    mars_baz = None
    if 'mars:BAZ' in origin:
        mars_baz = origin['mars:BAZ']['mars:value']
                
    # Signal to noise ratio
    snr = None
    if 'mars:snr' in origin:
        snr = float(origin['mars:snr']['@snrMQS'])

    # Create a new origin and add it to the list
    new_origin = Origin()
    new_origin.set_public_id(origin_id)
    new_origin.set_origin_time(origin_time)
    new_origin.set_latitude(latitude)
    new_origin.set_longitude(longitude)
    new_origin.set_depth(depth)
    new_origin.set_distance(mars_distance)
    new_origin.set_baz(mars_baz)
    new_origin.set_quality(_parse_quality(quality))
    new_origin.set_snr(snr)

    return new_origin

def _parse_magnitude(magnitude):
    """Parse the magnitude information"""
    if not isinstance(magnitude, dict):
        raise ValueError('Invalid magnitude type')
    
    _magnitude_id = magnitude['@publicID']
    _magnitude_type = magnitude['type']
    _mag_origin_id = magnitude['originID']

    if 'mag' in magnitude:
        _magnitude_value = magnitude['mag']['value']
        
        if 'lowerUncertainty' in magnitude['mag']:
            _magnitude_lower_uncertainty = magnitude['mag']['lowerUncertainty']
        else:
            _magnitude_lower_uncertainty = None

        if 'upperUncertainty' in magnitude['mag']:
            _magnitude_upper_uncertainty = magnitude['mag']['upperUncertainty']
        else:
            _magnitude_upper_uncertainty = None

        new_magnitude = Magnitude()
        new_magnitude.set_public_id(_magnitude_id)
        new_magnitude.set_type(_magnitude_type)
        new_magnitude.set_value(_magnitude_value)
        new_magnitude.set_lower_uncertainty(_magnitude_lower_uncertainty)
        new_magnitude.set_upper_uncertainty(_magnitude_upper_uncertainty)
        new_magnitude.set_origin_id(_mag_origin_id)
        return new_magnitude
    else:
        return None
    

def _parse_event(event):
    """Parse the event information"""
    # Get the event id
    public_id = event['@publicID']

    # Parse the event name
    event_name = _parse_event_name(event['description'])
    
    # Get the Mars event type
    mars_event_type = None
    if 'mars:type' in event:
        mars_event_type = _parse_event_type(event['mars:type'])

    # Get the Earth event type
    earth_event_type = None
    if 'type' in event:
        earth_event_type = event['type']

    # The preferred origin and magnitude
    if 'preferredOriginID' in event:
        preferred_origin_id = event['preferredOriginID']
    else:
        preferred_origin_id = None

    if 'preferredMagnitudeID' in event:
        preferred_magnitude_id = event['preferredMagnitudeID']
    else:
        preferred_magnitude_id = None

    # Parse the picks at the event level
    parsed_picks = []
    if 'pick' in event:
        picks = event['pick']
        if not isinstance(picks, list):
            picks = [picks]

        for pick in picks:
            _pick = _parse_pick(pick)
            parsed_picks.append(_pick)

    new_event = MarsEvent()
    new_event.set_public_id(public_id)
    new_event.set_event_name(event_name)
    new_event.set_mars_event_type(mars_event_type)
    new_event.set_earth_event_type(earth_event_type)
    new_event.set_preferred_origin_public_id(preferred_origin_id)
    new_event.set_preferred_magnitude_public_id(preferred_magnitude_id)
    new_event.set_picks(parsed_picks)

    return new_event

def _parse_pick(pick):
    """Parse the pick information"""
    if not isinstance(pick, dict):
        raise ValueError('Not a pick dictionary')
    
    # Get the pick id
    public_id = pick['@publicID']
    
    # Get the pick time
    time = UTCDateTime(pick['time']['value'])
    
    # Get the phase hint
    phase_hint = pick['phaseHint']
    
    # Get the lower uncertainty
    lower_uncertainty = None
    if 'lowerUncertainty' in pick['time']:
        lower_uncertainty = pick['time']['lowerUncertainty']
        
    # Get the upper uncertainty
    upper_uncertainty = None
    if 'upperUncertainty' in pick['time']:
        upper_uncertainty = pick['time']['upperUncertainty']
    
    new_pick = Pick()
    new_pick.set_public_id(public_id)
    new_pick.set_time(time)
    new_pick.set_phase_hint(phase_hint)
    new_pick.set_lower_uncertainty(lower_uncertainty)
    new_pick.set_upper_uncertainty(upper_uncertainty)
    
    return new_pick

def _parse_arrival(arrival):
    """Parse the arrival information"""
    if not isinstance(arrival, dict):
        raise ValueError('Not an arrival dictionary')
    
    # Get the arrival id
    public_id = arrival['@publicID']
    
    # The pick associated with the arrival
    pick_id = arrival['pickID']

    # Get the arrival time. None at first, will be set later
    # while associating with the picks.
    time = None # UTCDateTime(arrival['time']['value'])
    
    # Get the phase label
    phase_label = arrival['phase']
    
    # Get the lower uncertainty
    lower_uncertainty = None
    if 'lowerUncertainty' in arrival:
        lower_uncertainty = arrival['lowerUncertainty']
        
    # Get the upper uncertainty
    upper_uncertainty = None
    if 'upperUncertainty' in arrival:
        upper_uncertainty = arrival['upperUncertainty']
    
    new_arrival = Arrival()
    new_arrival.set_public_id(public_id)
    new_arrival.set_pick_id(pick_id)
    new_arrival.set_time(time)
    new_arrival.set_phase_label(phase_label)
    new_arrival.set_lower_uncertainty(lower_uncertainty)
    new_arrival.set_upper_uncertainty(upper_uncertainty)
    
    return new_arrival

def _associate_single_station_picks(event_obj, sst_picks):
    """ Associates the single station extension for Pick objects."""
    if not sst_picks or event_obj is None:
        return
    
    picks = event_obj.get_picks()
    for sst_pick in sst_picks:
        public_id = sst_pick['@publicID']

        if "sst:frequency" in sst_pick:
            frequency = sst_pick["sst:frequency"]["sst:value"]
            lower_uncertainty = sst_pick["sst:frequency"]["sst:lowerUncertainty"]
            upper_uncertainty = sst_pick["sst:frequency"]["sst:upperUncertainty"]

        else:
            frequency = None
            lower_uncertainty = None
            upper_uncertainty = None

        pick_reference = sst_pick['sst:pickReference']
        for pick in picks:
            if pick.get_public_id() == pick_reference:
                sst_pick_obj = SingleStationPick()
                sst_pick_obj.set_public_id(public_id)
                sst_pick_obj.set_frequency(frequency)
                sst_pick_obj.set_freq_lower_uncertainty(lower_uncertainty)
                sst_pick_obj.set_freq_upper_uncertainty(upper_uncertainty)
                pick.set_single_station_pick(sst_pick_obj)
                break

def read_catalog(catalog_file):
    """Parse a QuakeML catalog file"""
    logger.info(f'Reading catalog from {catalog_file}')
    _start_time = time.perf_counter()

    with open(catalog_file, 'r') as file:
        catalog = xmltodict.parse(file.read())

    # Get the list of events
    events = catalog['q:quakeml']['eventParameters']['event']

    # Get the single station information
    sst_origins = None
    sst_picks = None
    if 'sst:singleStationParameters' in catalog['q:quakeml']:
        sst_parameters = catalog['q:quakeml']['sst:singleStationParameters']
    
        # Single station origins
        if sst_parameters and 'sst:singleStationOrigin' in sst_parameters:
            sst_origins = sst_parameters['sst:singleStationOrigin']

        # Single station picks
        if sst_parameters and 'sst:singleStationPick' in sst_parameters:
            sst_picks = sst_parameters['sst:singleStationPick']
     
    # Loop through the events and parse the origins
    parsed_events = []
    for event in events:
        _event_obj = _parse_event(event)

        # Associate the single station picks with the event
        _associate_single_station_picks(_event_obj, sst_picks)
        
        # Get the origins
        origins = event['origin']

        # If there is only one origin, convert it to a list
        if not isinstance(origins, list):
            origins = [origins]

        # Loop through the origins and parse the information
        parsed_origins = []
        parsed_magnitudes = []
        
        # Origin information
        for origin in origins:
            # Parse the origin information and set the event as the parent
            _origin_obj = _parse_origin(origin)
            _origin_obj.set_parent_event(_event_obj)

            # Add the origin to the event
            parsed_origins.append(_origin_obj)
            
            # Parse the arrivals
            parsed_arrivals = []
            if 'arrival' in origin:
                arrivals = origin['arrival']
                if not isinstance(arrivals, list):
                    arrivals = [arrivals]

                for arrival in arrivals:
                    _arrival_obj = _parse_arrival(arrival)
                    _pick_obj = _event_obj.get_pick_for_arrival(_arrival_obj)
                    if _pick_obj:
                        _arrival_obj.set_time(_pick_obj.get_time())

                        # Get the lower/upper uncertainty
                        lower_uncertainty = _pick_obj.get_lower_uncertainty()
                        upper_uncertainty = _pick_obj.get_upper_uncertainty()

                        _arrival_obj.set_lower_uncertainty(lower_uncertainty)
                        _arrival_obj.set_upper_uncertainty(upper_uncertainty)

                        # Associate the SST Pick with the arrival
                        if _pick_obj.get_single_station_pick():
                            _arrival_obj.set_single_station_pick(
                                _pick_obj.get_single_station_pick())

                    parsed_arrivals.append(_arrival_obj)
            _origin_obj.set_arrivals(parsed_arrivals)

        # Magnitudes
        if 'magnitude' in event:
            magnitudes = event['magnitude']
            if not isinstance(magnitudes, list):
                magnitudes = [magnitudes]

            for magnitude in magnitudes:
                _magnitude_obj = _parse_magnitude(magnitude)
                if _magnitude_obj:
                    parsed_magnitudes.append(_magnitude_obj)
                
        # Store the magnitudes at the event level
        _event_obj.set_magnitudes(parsed_magnitudes)

        # Associate the magnitudes with the origins via the
        # originID attribute in the magnitude
        for magnitude in parsed_magnitudes:
            for origin in parsed_origins:
                if magnitude.get_origin_id() == origin.get_public_id():
                    origin.append_magnitude(magnitude)

        # Call the getter methods so that the event stores 
        # the preferred origin and magnitude. There is an 
        # internal check in these methods for None values.
        _ = _event_obj.get_preferred_magnitude()
        _ = _event_obj.get_preferred_origin()

        # Associate single station origins with the basic event description origins
        if sst_origins:
            for sst in sst_origins:
                for origin in parsed_origins:
                    if sst['sst:bedOriginReference'] == origin.get_public_id():
                        sst_params = SingleStationParameters()
                        sst_params.set_public_id(sst['@publicID'])
                        
                        distance = sst.get('sst:distance', {}).get(
                            'sst:distance', {}).get('sst:value')
                        pdf_distance = sst.get('sst:distance', {}).get(
                            'sst:distance', {}).get('sst:pdf', {})
                        azimuth = sst.get('sst:azimuth', {}).get(
                            'sst:azimuth', {}).get('sst:value')
                        pdf_azimuth = sst.get('sst:azimuth', {}).get(
                            'sst:azimuth', {}).get('sst:pdf', {})
                        
                        if distance:
                            sst_params.set_sst_distance(distance)
                            if pdf_distance:
                                sst_params.set_sst_distance_variable(
                                    pdf_distance.get('sst:variable'))
                                sst_params.set_sst_distance_pdf(
                                    pdf_distance.get('sst:probability'))
                        
                        if azimuth:
                            sst_params.set_sst_baz(azimuth)
                            if pdf_azimuth:
                                sst_params.set_sst_baz_variable(
                                    pdf_azimuth.get('sst:variable'))
                                sst_params.set_sst_baz_pdf(
                                    pdf_azimuth.get('sst:probability'))

                        origin.set_sst_parameters(sst_params)

        
        # Assign the origin to event
        _event_obj.set_origins(parsed_origins)

        # Store the event
        parsed_events.append(_event_obj)

        ## For testing
        # if _event.get_event_name() == 'S1415a':
        #     _event.report(include_picks=True)

    # Return the catalog
    _end_time = time.perf_counter()
    logger.ok(f'Success... Parsed {len(parsed_events)} events in {_end_time - _start_time:.2f} seconds')
    return Catalog(parsed_events, catalog_file)

