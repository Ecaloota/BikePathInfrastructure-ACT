import math

## Radius of spherical Earth, in metres
EARTH_RADIUS = 6371*1000

def to_radians(coordA : float) -> float:
    """
    Given a coordinate A, return A in radians.
    """

    return coordA * math.pi/180


def get_bearing(latA : float, longA : float, latB : float, longB : float) -> float:
    """
    Given two points A and B with latitude and longitude in radians, return the initial bearing
    from A to B in radians.
    """

    x = math.sin( longB - longA ) * math.cos( latB )
    y = math.cos( latA ) * math.sin( latB ) - math.sin( latA ) * math.cos( latB ) * math.cos( longB - longA )

    return math.atan2(x, y)


def haversine_distance(latA : float, longA : float, latB : float, longB : float) -> float:
    """
    Given two points A and B with latitude and longitude in radians, return the haversine distance
    between the two points in metres.
    """

    a = math.sin( (latB - latA) / 2 ) ** 2 + math.cos(latA) * math.cos(latB) * math.sin( ( longB - longA) / 2 ) ** 2
    c = 2 * math.atan2( math.sqrt( a ), math.sqrt( 1-a ) )
    haversine_distance = EARTH_RADIUS * c

    return haversine_distance
    

def cross_track_distance(latA : float, longA : float, latB : float, longB : float, latC : float, longC : float) -> float:
    """
    Given two points A and B with latitude and longitude in radians on a great circle, and a third point C, calculate 
    the (haversine?) distance between the point C and the great circle intersecting points A and B.
    """

    haversineAC = haversine_distance(latA, longA, latC, longC)
    bearingAC = get_bearing(latA, longA, latC, longC)
    bearingAB = get_bearing(latA, longA, latB, longB)

    return math.asin( math.sin( haversineAC / EARTH_RADIUS ) * math.sin( bearingAC - bearingAB ) ) * EARTH_RADIUS


def cross_arc_distance(latA : float, longA : float, latB : float, longB : float, latC : float, longC : float) -> float:
    """
    Given two points A and B with latitude and longitude in radians on a great circle, and a third point C, calculate 
    the (haversine?) distance between the point C and the great circle line segment joining points A and B.
    """

    bearingAB = get_bearing(latA, longA, latB, longB)
    bearingAC = get_bearing(latA, longA, latC, longC)
    haversineAC = haversine_distance(latA, longA, latC, longC)
    relative_bearing = abs(bearingAC - bearingAB)

    if relative_bearing > math.pi:
        relative_bearing = 2 * math.pi - relative_bearing

    ## Is relative bearing obtuse?
    if relative_bearing > math.pi/2:
        return haversineAC

    else:
        ## Fimd the cross-track distance
        dxt = cross_track_distance(latA, longA, latB, longB, latC, longC)

        ## Is Point D beyond the arc?
        haversineAB = haversine_distance(latA, longA, latB, longB)
        haversineAD = math.acos( math.cos( haversineAC / EARTH_RADIUS ) / math.cos( dxt / EARTH_RADIUS ) ) * EARTH_RADIUS

        if haversineAD > haversineAB:
            return haversine_distance(latB, longB, latC, longC)
        else:
            return abs(dxt)


## CASE 1
latA = -10.1 * math.pi/180
longA = -55.5 * math.pi/180
latB = -15.2 * math.pi/180
longB = -45.1 * math.pi/180
latC = -10.5 * math.pi/180
longC = -62.5 * math.pi/180

CASE1 = cross_arc_distance(latA, longA, latB, longB, latC, longC)
print("CASE1: ", CASE1)

## CASE 2
latA = 40.5 * math.pi/180
longA = 60.5 * math.pi/180
latB = 50.5 * math.pi/180
longB = 80.5 * math.pi/180
latC = 51.0 * math.pi/180
longC = 69.0 * math.pi/180

CASE2 = cross_arc_distance(latA, longA, latB, longB, latC, longC)
print("CASE2: ", CASE2)

## CASE 3
latA = 21.72 * math.pi/180
longA = 35.61 * math.pi/180
latB = 23.65 * math.pi/180
longB = 40.7 * math.pi/180
latC = 25 * math.pi/180
longC = 42 * math.pi/180

CASE3 = cross_arc_distance(latA, longA, latB, longB, latC, longC)
print("CASE3: ", CASE3)