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
    
    def update_location(self, lat: float, lon: float):
        self.lat = lat
        self.lon = lon
        (x, y, z) = coord_to_real((self.lat, self.lon))
        self.x = x
        self.y = y
        self.z = z

    def remove(self):
        self.tree.n = None
        self.tree = None
    
    def get_coord(self) -> tuple[float, float]:
        return (self.lat, self.lon)
    
    def get_pos(self) -> tuple[float, float, float]:
        return (self.x, self.y, self.z)

class octree:
    def __init__(self, x, y, z, radius):
        self.x = x
        self.y = y
        self.z = z
        self.radius = radius

        self.split = False
        self.n = None

        self.py_px_mz = None
        self.py_px_pz = None
        self.py_mx_pz = None
        self.py_mx_mz = None
        
        self.my_px_pz = None
        self.my_px_mz = None
        self.my_mx_pz = None
        self.my_mx_mz = None
        pass

    def inside(self, p):
         return (self.x - self.radius <= p[0] <= self.x + self.radius and
                 self.y - self.radius <= p[1] <= self.y + self.radius and
                 self.z - self.radius <= p[2] <= self.z + self.radius)
    
    def sphere_intersecting_cube(self, sphere_x, sphere_y, sphere_z, sphere_radius):
        closest_x = max(self.x - self.radius, min(sphere_x, self.x + self.radius))
        closest_y = max(self.y - self.radius, min(sphere_y, self.y + self.radius))
        closest_z = max(self.z - self.radius, min(sphere_z, self.z + self.radius))
        distance = math.sqrt((closest_x - sphere_x) ** 2 +
                            (closest_y - sphere_y) ** 2 +
                            (closest_z - sphere_z) ** 2)
        return distance <= sphere_radius
    
    def point_in_sphere(self, sphere_x, sphere_y, sphere_z, sphere_radius):
        x, y, z = self.n.get_pos()
        distance = math.sqrt((x - sphere_x) ** 2 +
                            (y - sphere_y) ** 2 +
                            (z - sphere_z) ** 2)
        return distance <= sphere_radius
    
    def find(self, pos: tuple[float, float, float]):
        if not self.split:
            if self.n != None:
                if self.point_in_sphere(pos[0], pos[1], pos[2], RANGE):
                    return [self.n]
                return []
            return []
        out = []
        out.append(self.py_px_pz.find(pos))
        out.append(self.py_px_mz.find(pos))
        out.append(self.py_mx_pz.find(pos))
        out.append(self.py_mx_mz.find(pos))

        out.append(self.my_px_pz.find(pos))
        out.append(self.my_px_mz.find(pos))
        out.append(self.my_mx_pz.find(pos))
        out.append(self.my_mx_mz.find(pos))
        return out

    def insert(self, n: node):
        if not self.inside(n.get_pos()):
            return
        
        if not self.split:
            if self.n == None:
                self.n = n
                self.n.tree = self
                return
            self.split()
            self.insert(self.n)
            self.n = None
            self.insert(n)
            return

        self.py_px_pz.insert(n)
        self.py_px_mz.insert(n)
        self.py_mx_pz.insert(n)
        self.py_mx_mz.insert(n)
        
        self.my_px_pz.insert(n)
        self.my_px_mz.insert(n)
        self.my_mx_pz.insert(n)
        self.my_mx_mz.insert(n)

    def split(self):
        self.split = True
        new_radius = self.radius / 2
        offsets = [-new_radius, new_radius]

        self.py_px_pz = octree(self.x + offsets[1], self.y + offsets[1], self.z + offsets[1], new_radius)
        self.py_px_mz = octree(self.x + offsets[1], self.y + offsets[1], self.z + offsets[0], new_radius)
        self.py_mx_pz = octree(self.x + offsets[0], self.y + offsets[1], self.z + offsets[1], new_radius)
        self.py_mx_mz = octree(self.x + offsets[0], self.y + offsets[1], self.z + offsets[0], new_radius)
        self.my_px_pz = octree(self.x + offsets[1], self.y + offsets[0], self.z + offsets[1], new_radius)
        self.my_px_mz = octree(self.x + offsets[1], self.y + offsets[0], self.z + offsets[0], new_radius)
        self.my_mx_pz = octree(self.x + offsets[0], self.y + offsets[0], self.z + offsets[1], new_radius)
        self.my_mx_mz = octree(self.x + offsets[0], self.y + offsets[0], self.z + offsets[0], new_radius)

    def remove(self, n):
        pass