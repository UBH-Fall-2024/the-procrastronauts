import math

RANGE = 12        #maximum distance for communication in meters
ER = 6366707.0195 #Earth Radius in Meters

# https://en.wikipedia.org/wiki/Haversine_formula
def haversine(p1, p2):
    a = math.sin(((p1[1]-p2[1])*math.pi/180)/2)**2
    b = math.cos(p1[1]*math.pi/180)
    c = math.cos(p2[1]*math.pi/180)
    d = math.sin(((p1[0]-p2[0])*math.pi/180)/2)**2
    return 2*ER*math.asin(math.sqrt(a+(b*c*d)))

def coord_to_real(coord):
    x = ER * math.cos(coord[1]) * math.cos(coord[0])
    y = ER * math.cos(coord[1]) * math.sin(coord[0])
    z = ER * math.sin(coord[1])
    return (x, y, z)

class node:
    def __init__(self, id, lat, lon):
        self.id = id
        self.update_location(lat, lon)
        self.tree = None
    
    def update_location(self, lat, lon):
        self.lat = lat
        self.lon = lon
        (x, y, z) = coord_to_real((self.lat, self.lon))
        self.x = x
        self.y = y
        self.z = z
    
    def get_coord(self):
        return (self.lat, self.lon)
    
    def get_pos(self):
        return (self.x, self.y, self.z)

class octree:

    def __init__(self, tl, tr, bl, br):
        pass

    def insert(self, n):
        pass

    def remove(self, n):
        pass