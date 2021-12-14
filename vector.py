import math

""" 2-dimensional vector class """
class Vec:
    def __init__(self, x, y = None):
        self.set(x, y)

    def set(self, x, y = None):
        if y == None:
                # if two arguments, then use them as components
            try:
                self.x = x.x
                self.y = x.y
            except:
                self.x = x[0]
                self.y = x[1]
                
        else:
            # if one argument, assume it's a vector & copy its components
            self.x = x
            self.y = y
            
    def set_polar(self, r, theta):
        self.x = r * math.cos(math.radians(theta))
        self.y = r * math.sin(math.radians(theta))
    
    def __add__(self, v):
        return Vec(self.x + v.x, self.y + v.y)
    
    def __sub__(self, v):
        return Vec(self.x - v.x, self.y - v.y)
    
    def __mul__(self, c):
        return Vec(self.x * c, self.y * c)
    
    def __rmul__(self, c):
        return self.__mul__(c)
    
    def __truediv__(self, c):
        return Vec(self.x / c, self.y / c)
    
    def __floordiv__(self, c):
        return Vec(self.x / c, self.y / c)
    
    def __eq__(self, v):
         return self.x == v.x and self.y == v.y
        
    def __neg__(self):
        return Vec(-self.x, -self.y)

    def __str__(self):
        return "({x}, {y})".format(x = self.x, y = self.y)
    
    def get_mag(self):
        return math.sqrt(self.x**2 + self.y**2)

    def get_angle(self):
        return math.degrees(math.atan2(self.y, self.x))
    
    """ Get the normalized vector, keeping the ratio of the components """
    def norm(self):
        mag = self.get_mag()
        if mag == 0:
            return Vec(0, 0)
        return Vec(self.x / mag, self.y / mag)
    
