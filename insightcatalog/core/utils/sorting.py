# -*- coding: utf-8 -*-

def sort_events_by_distance(event_names, distances):
    """ Sorts the given event names by distance."""
    # Pairing events with their respective distances
    paired_list = list(zip(event_names, distances))
    
    # Sorting the paired list by distance (second element of the tuples)
    sorted_paired_list = sorted(paired_list, key=lambda x: x[1])
    
    # Extracting sorted events from the sorted list of tuples
    sorted_event_names = [event for event, _ in sorted_paired_list]
    sorted_distances = [distance for _, distance in sorted_paired_list]
    
    return sorted_event_names, sorted_distances
