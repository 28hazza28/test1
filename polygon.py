from asyncio.windows_events import NULL
import math
import enum
from pickle import FALSE, TRUE


class PrimitiveType(enum.Enum):
    points = 1
    lines = 2
    triangles = 3

class Point3D(object):
    x:float = 0
    y:float = 0
    z:float = 0
    def __init__(self,_x:float,_y:float,_z:float):
        self.x = _x
        self.y = _y
        self.z = _z

    def normalyse(self):
        mod = abs(self.x*self.x)+abs(self.y*self.y)+abs(self.z*self.z)
        norm = math.sqrt(mod)
        if norm!=0:
            self.x /=norm
            self.y /=norm
            self.z /=norm
        return Point3D(self.x,self.y,self.z)
    def ToString(self):
        return str(self.x)+" "+str(self.y)+" "+str(self.z)

    def __add__(self, other):
        x = self.x + other.x
        y = self.y + other.y
        z = self.z + other.z
        return Point3D(x,y,z)

    def __sub__(self, other):
        x =  self.x- other.x
        y = self.y - other.y
        z = self.z - other.z
        #self.x-=other.x
        #self.y-=other.y
        #self.z-=other.z
        return Point3D(x,y,z)

    def Clone(self):
        return Point3D(self.x,self.y,self.z)

    

class Polygon3D(object):
    vert_arr:list[Point3D] 
    n:Point3D
    def __init__(self,_vert_arr:list[Point3D]):
        self.n = NULL
        self.vert_arr = _vert_arr
        if (len(_vert_arr) > 2):
            self.n = self.compNorm(_vert_arr[0],_vert_arr[1],_vert_arr[2])

    def compNorm(self, p3:Point3D,p2:Point3D,p1:Point3D):
        v = Point3D(p3.x-p1.x,p3.y-p1.y,p3.z-p1.z)
        u = Point3D(p2.x-p1.x,p2.y-p1.y,p2.z-p1.z)
        v = v.normalyse()
        u = u.normalyse()
        Norm = Point3D(
            u.y * v.z - u.z * v.y,
            u.z * v.x - u.x * v.z,
            u.x * v.y - u.y * v.x)
        
        Norm.normalyse()
        return Point3D(Norm.x,Norm.y,Norm.z)
    
    
    
    def affilationPoint(self, p: Point3D):
        if (len(self.vert_arr)<3):
            return FALSE
        a = self.vert_arr [0].Clone()
        b = self.vert_arr [1].Clone()
        c = self.vert_arr [2].Clone()
        p = p.Clone()
        p = p - a
        b = b - a
        c = c - a

        m =  (p.x*b.y - b.x*p.y)/(c.x*b.y - b.x*c.y)
        if(m >=0 and m <=1):
            l = (p.x - m*c.x)/b.x
            if (l >=0 and m+l <=1):
                return TRUE
        return FALSE

    def project_point(self,p: Point3D):
        p1 = self.vert_arr [0]
        d = -(self.n.x*p1.x + self.n.y*p1.y + self.n.z*p1.z)
        z = (-d - self.n.x*p.x- self.n.y*p.y)/self.n.z
        return Point3D(p.x, p.y, z)




    
        
    

class Mesh3D(object):
    polygons:list[Polygon3D] = []

    def __init__(self,_points:list[Point3D], prim_type: PrimitiveType):
        self.polygons = []
        if _points!=None:
            if (prim_type == PrimitiveType.points ):
                
                for i in range (len(_points)):
                    vert_array = []
                    vert_array.append(_points[i])
                    self.polygons.append(Polygon3D(vert_array))

            elif (prim_type == PrimitiveType.lines):
                for i in range (len(_points)-1):
                    vert_array = []
                    vert_array.append(_points[i])
                    vert_array.append(_points[i+1])
                    self.polygons.append(Polygon3D(vert_array)) 

            elif (prim_type == PrimitiveType.triangles):
                for i in range (int(len(_points)/3)):
                    vert_array = []
                    vert_array.append(_points[3*i])
                    vert_array.append(_points[3*i+1])
                    vert_array.append(_points[3*i+2])
                    self.polygons.append(Polygon3D(vert_array))

        
       