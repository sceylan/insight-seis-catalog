# *-* coding: utf-8 *-*
import cartopy.crs as ccrs
import cartopy.geodesic as cgeo
import numpy as np

def degrees2km(degrees, radius=3389.5):
    """ Convert degrees to kilometers on Mars. """
    return degrees * (radius * 2 * np.pi / 360)

def km2degrees(km, radius=3389.5):
    """Convert kilometers to degrees on Mars. """
    return km / (radius * 2 * np.pi / 360)

def distbaz2lonlat(distance, backazimuth, origin_lat=4.502384, 
                   origin_lon=135.623447, radius=3389.5, 
                   flattening=0.00589):
    """
    Compute latitude and longitude on Mars given origin coordinates, 
    distance, and backazimuth. The distance and the backazimuth are 
    in degrees. Returns a tuple of (latitude, longitude) on Mars.
    """
    # Convert distance to meters
    distance = 1000.0 * degrees2km(distance, radius)
    
    # Create a Geodesic object for Mars with the specified radius.
    # Radius is in meters, so we multiply by 1000.
    mars_geodesic = cgeo.Geodesic(
        radius=radius*1000, flattening=flattening)

    # Perform direct geodesic calculation. 
    destination = mars_geodesic.direct(
        (origin_lon, origin_lat), azimuths=backazimuth, 
        distances=distance)
    
    # Return the longitude and latitude in this order.
    # destination in this case is a numpy ndarray in the form
    # of [[ 65.80319358 -10.06693661  83.59460779]], for instance.
    return destination[0][0], destination[0][1]


def latlon2distbaz(destination_lat, destination_lon, 
                   origin_lat=4.502384, origin_lon=135.623447,
                   radius_in_km=3389.5, flattening=0.00589):
    """
    Compute distance and backazimuth on Mars given origin and 
    destination coordinates. 
    
    The return value is a tuple of (distance, backazimuth). 
    The distance is converted to degrees assumin a spherical planet.
    """
    # Create a Geodesic object for Mars with the specified radius
    mars_geodesic = cgeo.Geodesic(radius=radius_in_km*1000, flattening=flattening)

    # Perform inverse geodesic calculation
    result = mars_geodesic.inverse(
        endpoints=[(origin_lon, origin_lat)],
        points=[(destination_lon, destination_lat)])
        
    # result = mars_geodesic.inverse(
    #     lon1=origin_lon, lat1=origin_lat, 
    #     lon2=destination_lon, lat2=destination_lat)

    # Convert distance to degrees and return the results
    # return km2degrees(result.distance / 1000.0), result.azimuth1
    return km2degrees(result[0][0]), result[0][1]


