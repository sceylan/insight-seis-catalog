# -*- coding: utf-8 -*-
import datetime
from obspy import UTCDateTime
import uuid
from dateutil import parser

def to_datetime(timestamp):
    """
    Parse timestamp into a datetime object, handling various formats.
    
    Parameters:
    - timestamp: datetime or string
    
    Returns:
    - datetime.datetime object
    """
    if isinstance(timestamp, datetime.datetime) or isinstance(timestamp, UTCDateTime):
        # Already a datetime object, return as is
        return timestamp
    
    elif isinstance(timestamp, str):
        # Try to parse using dateutil.parser
        # This would handle the ISO 8601 format and many others
        try:
            return parser.parse(timestamp)
        except ValueError:
            pass

        # Handle common date formats manually if parser fails
        formats = [
            "%Y-%m-%d %H:%M:%S.%f",
            "%Y-%m-%dT%H:%M:%S.%fZ",
            "%Y-%m-%d %H:%M:%S",
            "%Y-%m-%dT%H:%M:%S",
            "%Y/%m/%d %H:%M:%S",
            "%d-%m-%Y %H:%M:%S",
            "%m/%d/%Y %H:%M:%S",
            "%Y%m%d%H%M%S",
        ]
        for fmt in formats:
            try:
                return datetime.datetime.strptime(timestamp, fmt)
            except ValueError:
                continue
        
        raise ValueError(f"Unrecognized date string format: {timestamp}")
    else:
        raise TypeError("timestamp must be datetime, obspy.UTCDateTime or a string")
    

def generate_object_id(namespace, object_type, object_timestamp):
    """
    Generate a unique object ID for a Mars catalog component.
    Example: smi:insight.mqs/Origin/20221125095034.947861.136787

    Parameters:
    - namespace (str): e.g., 'smi:insight.mqs'
    - object_type (str): e.g., 'Origin', 'Arrival', 'Pick'
    - event_time (datetime.datetime, str, or float/int): Event time

    Returns:
    - str: Generated object ID
    """
    # Parse the event_time into a datetime object
    dt = to_datetime(object_timestamp)

    # Format time as YYYYMMDDHHMMSS.ffffff
    time_str = dt.strftime("%Y%m%d%H%M%S.%f")
    
    # Generate a unique component using UUID, keeping only digits for brevity
    unique_component = str(uuid.uuid4().int)[:6]

    # Combine all parts
    object_id = f"{namespace}/{object_type}/{time_str}.{unique_component}"

    return object_id

