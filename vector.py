import math

""" 2-dimensional vector class """
class Vec:

    @staticmethod
    def polar(r, theta):
        vec = Vec(math.cos(math.radians(theta)),
                  math.sin(math.radians(theta))) * r
        return vec

    def __init__(self, x, y = None):
        self.set(x, y)

    def set(self, x, y=None):
        if y is None:
            # if two arguments, then use them as components
            try:
                self.x = x.x
                self.y = x.y
            except AttributeError:
                self.x = x[0]
                self.y = x[1]
        else:
            # if one argument, assume it's a vector & copy its components
            self.x = x
            self.y = y
    
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

    def mag(self):
        return math.sqrt(self.x**2 + self.y**2)

    def angle(self):
        return -math.degrees(math.atan2(self.y, self.x))

    def rounded(self):
        return Vec(round(self.x), round(self.y))
    
    """ Get the normalized vector, keeping the ratio of the components """
    def norm(self):
        mag = self.mag()
        if mag == 0:
            return Vec(0, 0)
        return Vec(self.x / mag, self.y / mag)
    
    def dist(self, v):
        return math.hypot(self.x - v.x, self.x - v.x)

    def tuple(self):
        return (self.x, self.y)
    
    def __str__(self):
        return "({x}, {y})".format(x = round(self.x, 1), y = round(self.y, 1))
    
