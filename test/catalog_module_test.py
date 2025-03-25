#! /usr/bin/env python
# -*- coding: utf-8 -*-
import matplotlib.pyplot as plt
import insightcatalog as icat

# Read the catalog
catalog = icat.read_catalog('../insightcatalog/data/events_mars_extended_multiorigin_v14_2023-01-01.xml')

# We can sub-select the events that will be used
catalog = catalog.select(mars_event_types=['BB', 'LF'])

# Also possible to get an event by its name
event = catalog.get_event_by_name('S1222a')

# Print a comprehensive report
event.report(include_picks=True, include_magnitudes=True, include_arrivals=True)

# Get the phase arrivals for the preferred origin
arrivals = event.get_preferred_origin().get_arrivals()

# An example using the arrivals: Collect the R1 arrivals and plot the dispersion curve
r1_arrivals = [arrival for arrival in arrivals if arrival.get_phase_label() == 'R1']

# Get the origin time
origin_time = event.get_preferred_origin().get_origin_time()

# Travel times for the R1 phase picks
ttimes = [arrival.get_time() - origin_time for arrival in r1_arrivals]

# There are two ways to get the frequency of the R1 phase picks
# 1. Using the SingleStationPick object of the Arrival object
# 2. Using directly the Arrival object, which is a wrapper around the SingleStationPick object
freqs = [arrival.get_frequency() for arrival in r1_arrivals]

# Sort the travel times by frequency
sorted_ttimes = [arrival for _, arrival in sorted(zip(freqs, ttimes))]
sorted_freqs = sorted(freqs)

# Plot the dispersion curve
plt.plot(sorted_freqs, sorted_ttimes, 'o-')
plt.xlabel('Frequency (Hz)')
plt.ylabel('Time after origin (s)')
plt.title('R1 travel time curve for event S1222a')
plt.show()
