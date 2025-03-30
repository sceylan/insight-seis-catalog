#! /usr/bin/env python
# -*- coding: utf-8 -*-
import insightcatalog as icat

# Read the catalog
catalog = icat.read_catalog('../data/events_mars_extended_multiorigin_v14_2023-01-01.xml')

# Filter events by a list of event names. For the sake of this example, 
# we are using two of the confirmed impacts. This method would work for
# any event in the catalog. For more information on impacts, see these papers:  
#
#   Daubar et al. (2023) Planet. Sci. J., doi:10.3847/PSJ/ace9b4 
#   Posiolova et al. (2022) Science, doi:10.1126/science.abq7704
#   Garcia et al. (2022) Nat. Geosci., https://doi.org/10.1038/s41561-022-01014-0
#   Charalambous et al. (2025) GRL, https://doi.org/10.1029/2024GL110159
impact_event_names = ['S0986c', 'S0981c']
impacts = catalog.get_list_of_events_by_name(impact_event_names)


# Extract more information about the event's location. If MQS calculated any 
# of these parameters, they will be avaliable in the single station extension (SST) 
# under an Origin object.
for event in impacts:
    print(f"Event: {event.get_event_name()}")

    for origin_idx, origin in enumerate(event.get_origins()):
        # SST parameters object
        sst = origin.get_sst_parameters()

        # Operator assigned parameters
        distance = origin.get_distance()
        baz = origin.get_baz()

        # Parameters assigned after MQS location inversion
        sst_distance = sst.get_sst_distance()
        sst_baz = sst.get_sst_baz()

        # Print the event name and the extracted parameters
        event_name = event.get_event_name()
        print(f"\tOrigin: {origin_idx}     Distance: {distance}, Baz: {baz}, " + \
            f"SST Distance: {sst_distance}, SST Baz: {sst_baz}")
        