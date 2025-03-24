#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
UTC/LMST utility methods. Developed for InSight mission to Mars.
"""
from __future__ import print_function

import datetime as dt
import numpy as np
from obspy import UTCDateTime

# Sol0 start - Insight landing.
# Value is from the JPL URL below for Sol 0:
# https://naif.jpl.nasa.gov/cgi-bin/chronos_nsyt.pl?setup=nsyttime
REFERENCE_TIME_INSIGHT_LANDING = UTCDateTime("2018-11-26T05:10:50.336037Z")

# Sol-001 and Sol-002 start times to compute one Martian day in seconds.
# Cannot use landing time because Sol-000 lasted shorter.
SOL01_START_TIME = UTCDateTime("2018-11-27T05:50:25.580014Z")
SOL02_START_TIME = UTCDateTime("2018-11-28T06:30:00.823990Z")

# Compute one martian day in seconds with a microsecond correction
# to avoid falling into previous or next sol instead of current
# one at sol midnights
SECONDS_PER_MARS_DAY = SOL02_START_TIME - SOL01_START_TIME - 0.000005

# Earth days in seconds
SECONDS_PER_EARTH_DAY = 86400.


def lmst_to_utc(lmst_time, sol0_start_utc=REFERENCE_TIME_INSIGHT_LANDING):
    """
    Returns corresponding UTC date/time for a given LMST value. LMST can
    be a float or UTCDateTime instance. LMST variable should take Linux
    epoch as basis.

    Return value is an UTCDateTime instance.
    """
    _mars_to_earth = float(lmst_time) / SECONDS_PER_EARTH_DAY + 1

    _utc_time = UTCDateTime(
        _mars_to_earth * SECONDS_PER_MARS_DAY + float(sol0_start_utc))

    return _utc_time


def utc_to_lmst(utc_time, sol0_start_utc=REFERENCE_TIME_INSIGHT_LANDING,
                sol_dtype='int'):
    """
    Convert UTC to LMST. Default sol-0 time is InSight landing time
    in UTC. Returned LMST counts from Linux epoch; date value showing
    the sol number.

    Return value is a tuple of LMST as UTCDateTime instance and sol number.
    Sol number can be integer or float. If float, it includes decimal
    fractions of sol as well.
    """
    # Cast to UTCDateTime, if datetime is given. This is useful to avoid
    # long type casting statements while plotting
    if isinstance(utc_time, dt.datetime):
        utc_time = UTCDateTime(utc_time)

    _elapsed_mars_days = (utc_time - sol0_start_utc) / SECONDS_PER_MARS_DAY

    _time = UTCDateTime((_elapsed_mars_days - 1) * SECONDS_PER_EARTH_DAY)

    # Return a tuple with local Mars time as UTCDateTime and sol number
    if sol_dtype == 'float' or sol_dtype is None:
        return _time, _elapsed_mars_days
    else:
        # Note the floor function to get the sol number because the first sol is 0
        return _time, int(np.floor(_elapsed_mars_days))


def utc_to_sol(utc_time, sol0_start_utc=REFERENCE_TIME_INSIGHT_LANDING,
               sol_dtype='int'):
    """
    A short hand call to utc2lmst method to get sol number. Return value
    is the sol number as integer or float, depending on sol_dtype.

    sol_dtype is type of string.
    """
    _, sol_number = utc_to_lmst(
        utc_time=utc_time, sol0_start_utc=sol0_start_utc, sol_dtype=sol_dtype)

    return sol_number


def sol_span_in_utc(sol, sol0_start_utc=REFERENCE_TIME_INSIGHT_LANDING):
    """Returns start and end times in UTC for a given sol. """
    utc_representation = \
        UTCDateTime(sol * SECONDS_PER_MARS_DAY) + float(sol0_start_utc)

    return utc_representation, utc_representation + SECONDS_PER_MARS_DAY
