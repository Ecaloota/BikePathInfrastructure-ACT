#import math
import numpy as np
import pandas as pd

## Radius of spherical Earth, in metres
EARTH_RADIUS = 6371*1000

def get_bearing_vectorised(latA, longA, latB, longB):
    """
    Given two points A and B with latitude and longitude in radians, return the initial bearing
    from A to B in radians.
    """

    # TODO: Write a test for this.
    dlong = longB - longA

    x = np.sin( dlong ) * np.cos( latB )
    y = np.cos( latA ) * np.sin( latB ) - np.sin( latA ) * np.cos( latB ) * np.cos( dlong )

    return np.arctan2(x, y)


def haversine_vectorised(latA, longA, latB, longB):
    """
    Given two points A and B with latitude and longitude in radians, return the haversine distance
    between the two points in metres. Vectorised for np.

    i.e. haversine_vectorised(df1['x_lat'].values, df1['x_long'].values, df2['y_lat'].values, df2['y_long'].values)
    """

    # TODO: Write a test for this.

    a = np.sin( ( latB - latA ) / 2 ) ** 2 + np.cos(latA) * np.cos(latB) * np.sin( ( longB - longA ) / 2 ) ** 2
    c = 2 * np.arctan2( np.sqrt( a ), np.sqrt( 1-a ) )
    haversine_distance = EARTH_RADIUS * c

    return haversine_distance


def cross_track_distance_vectorised(latA, longA, latB, longB, latC, longC):
    """
    Given two points A and B with latitude and longitude in radians on a great circle, and a third point C, calculate 
    the haversine distance between the point C and the great circle intersecting points A and B.
    """
    # TODO: Write a test for this.
    
    haversineAC = haversine_vectorised(latA, longA, latC, longC)
    bearingAC = get_bearing_vectorised(latA, longA, latC, longC)
    bearingAB = get_bearing_vectorised(latA, longA, latB, longB)

    return np.arcsin( np.sin( haversineAC / EARTH_RADIUS ) * np.sin( bearingAC - bearingAB ) ) * EARTH_RADIUS


def cross_arc_distance_vectorised(latA, longA, latB, longB, latC, longC, max_consideration_distance = 1000):
    """
    Given two points A and B with latitude and longitude in radians on a great circle, and a third point C, calculate 
    the haversine distance between the point C and the great circle line segment joining points A and B.
    """

    # TODO: Write a test for this.

    ## We consider every path to each particular light

    ## Make a results array that we can return. It will contain the shortest (cross-arc) distance between every 
    ## pair of points and the particular light of interest. This will be a column vector initialised with np.inf
    result = np.full(np.shape(latA), np.inf) 

    ## Calculate the two bearing arrays AB and AC, and compute the relative bearing array
    bearingAB = get_bearing_vectorised(latA, longA, latB, longB)
    bearingAC = get_bearing_vectorised(latA, longA, latC, longC)
    relative_bearing = np.abs(bearingAC - bearingAB)

    ## Calculate the haversine AC distance array
    haversineAC = haversine_vectorised(latA, longA, latC, longC)

    ## Are elements in the relative bearing array in the correct quadrant?

    # At positions where the relative bearing is greater than pi in the relative bearing array,
    # change the value to 2pi - the current value at those positions where relative bearing is 
    # greater than pi

    # TODO: Write a test for this!
    relative_bearing[relative_bearing > np.pi] = 2 * np.pi - relative_bearing[relative_bearing > np.pi]

    ## Are elements in the relative bearing array, obtuse?
    ## If so, set result array element at the corresponding positions to haversineAC

    # TODO: Write a test for this!
    result[relative_bearing > np.pi/2] = haversineAC[relative_bearing > np.pi/2]

    ## Find the cross-track distance array
    dxt = cross_track_distance_vectorised(latA, longA, latB, longB, latC, longC)

    ## Is pointD beyond the arc?
    haversineAB = haversine_vectorised(latA, longA, latB, longB)
    haversineBC = haversine_vectorised(latB, longB, latC, longC)
    haversineAD = np.arccos( np.cos( haversineAC / EARTH_RADIUS ) / np.cos( dxt / EARTH_RADIUS ) ) * EARTH_RADIUS

    ## Are the elements of the haversineAD array larger than the haversineAB array?
    ## If the elements of haversineAD > the corresponding elements of haversineAB
    ## return haversineBC at those positions
    result[haversineAD > haversineAB] = haversineBC[haversineAD > haversineAB]
    
    ## Else if haversineAD < haversineAB, return the absolute value of dxt at those positions
    result[haversineAD < haversineAB] = np.abs(dxt[haversineAD < haversineAB])

    return result