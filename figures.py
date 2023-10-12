import mathLib as ml
from math import tan, pi, atan2, acos

class Intercept(object):
    def __init__(self, distance, point, texcoords, normal, obj):
        self.distance = distance
        self.point = point
        self.normal = normal
        self.texcoords = texcoords
        self.obj = obj

class Shape(object):
    def __init__(self,position,material):
        self.position = position
        self.material = material

    def ray_intersect(self,orig,dir):
        return None

class Sphere(Shape):
    def __init__(self,position,radius,material):
        self.radius = radius
        super().__init__(position,material)
        
    def ray_intersect(self, orig, dir):
        l = ml.substractV(self.position, orig)
        lengthL = ml.magV(l)
        tca = ml.dotProd(l,dir)
        
        #if radius < d: no hay contacto (False)
        #if radius > d: si hay contacto (True)
        
        #Da una raiz negativa, tal vez por eso no se traza el ovalo
        d = (lengthL**2 - tca**2)**0.5
        if d > self.radius:
            return None
        
        thc = (self.radius**2 - d**2)**0.5
        t0 = tca - thc
        t1 = tca + thc
        
        if t0<0:
            t0 = t1
        if t0<0:
            return None
        
        #P = O+D*t0
        p = ml.addV(orig,ml.VxE(dir, t0))
        normal = ml.substractV(p,self.position)
        normal = ml.normalizeV(normal)
        
        u = (atan2(normal[2], normal[0]) / (2*pi)) + 0.5
        v = acos(normal[1]) / pi
        
        return Intercept(distance = t0,
                         point = p,
                         normal = normal,
                         texcoords= (u,v),
                         obj = self)

class Plane(Shape):
    def __init__(self, position, normal, material):
        self.normal = ml.normalizeV(normal)
        super().__init__(position, material)
    
    def ray_intersect(self, orig, dir):
        #Distancia = (planePos - origRay) o normal) / (dirRay o normal)
        
        denom = ml.dotProd(dir, self.normal)
        
        if abs(denom) <= 0.0001:
            return None
        
        num = ml.dotProd(ml.substractV(self.position, orig), self.normal)
        t = num/denom
        
        if t<0:
            return None
        
        #P = O+D*t0
        p = ml.addV(orig, ml.VxE(dir,t))
        
        return Intercept(distance = t,
                         point = p,
                         normal = self.normal,
                         texcoords= None,
                         obj = self)

class Disk(Plane):
    def __init__(self, position, normal, radius, material):
        self.radius = radius
        super().__init__(position, normal, material)
    
    def ray_intersect(self, orig, dir):
        planeIntersect = super().ray_intersect(orig, dir)
        
        if planeIntersect is None:
            return None
        
        contactDistance = ml.substractV(planeIntersect.point, self.position)
        contactDistance = ml.magV(contactDistance)
        
        if contactDistance > self.radius:
            return None
        
        return Intercept(distance = planeIntersect.distance,
                         point = planeIntersect.point,
                         normal = self.normal,
                         texcoords= None,
                         obj = self)

class AABB(Shape):
    #Axis Aligned Bounding Box
    #Cajas sin rotacion
    
    #En Minecraft, los cubos solo tienen posicion; ni escala, ni rotacion.
    
    def __init__(self, position, size, material):
        self.size = size
        super().__init__(position, material)
        
        self.planes=[]
        
        self.size = size
        
        #Sides
        leftPlane = Plane(ml.addV(self.position, (-self.size[0]/2,0,0)), (-1,0,0), material)
        rightPlane = Plane(ml.addV(self.position, (self.size[0]/2,0,0)), (1,0,0), material)
        
        bottomPlane = Plane(ml.addV(self.position, (0,-self.size[1]/2,0)), (0,-1,0), material)
        topPlane = Plane(ml.addV(self.position, (0,self.size[1]/2,0)), (0,1,0), material)
        
        backPlane = Plane(ml.addV(self.position, (0,0,-self.size[2]/2)), (0,0,-1), material)
        frontPlane = Plane(ml.addV(self.position, (0,0,self.size[2]/2)), (0,0,1), material)

        self.planes.append(leftPlane)
        self.planes.append(rightPlane)
        self.planes.append(bottomPlane)
        self.planes.append(topPlane)
        self.planes.append(backPlane)
        self.planes.append(frontPlane)
        
        #Bounding Box (agregar limites a los planos infinitos creados)
        self.boundsMin = [0,0,0]
        self.boundsMax = [0,0,0]
        
        bias = 0.001
        
        for i in range (3):
            self.boundsMin[i] = self.position[i]-(bias+size[i]/2)
            self.boundsMax[i] = self.position[i]+(bias+size[i]/2)
    
    def ray_intersect(self, orig, dir):
        intersect = None
        t = float('inf')
        
        u = 0
        v = 0
        
        for plane in self.planes:
            planeIntersect = plane.ray_intersect(orig,dir)
            
            if planeIntersect is not None:
                planePoint = planeIntersect.point
                
                if self.boundsMin[0] < planePoint[0] < self.boundsMax[0]:
                    if self.boundsMin[1] < planePoint[1] < self.boundsMax[1]:
                        if self.boundsMin[2] < planePoint[2] < self.boundsMax[2]:
                            if planeIntersect.distance < t:
                                t = planeIntersect.distance
                                intersect = planeIntersect
                                
                                #Generar uv's
                                if abs(plane.normal[0]) > 0:
                                    #Este es un plano izquierdo o derecho
                                    #Usar Y y Z para crear uv's, estando en X.
                                    u = (planePoint[1] - self.boundsMin[1]) / (self.size[1]+0.002)
                                    v = (planePoint[2] - self.boundsMin[2]) / (self.size[2]+0.002)
                                elif abs(plane.normal[1]) > 0:
                                    #Usar X y Z para crear uv's, estando en Y.
                                    u = (planePoint[0] - self.boundsMin[0]) / (self.size[0]+0.002)
                                    v = (planePoint[2] - self.boundsMin[2]) / (self.size[2]+0.002)
                                elif abs(plane.normal[2]) > 0:
                                    #Usar X y Y para crear uv's, estando en Z.
                                    u = (planePoint[0] - self.boundsMin[0]) / (self.size[0]+0.002)
                                    v = (planePoint[1] - self.boundsMin[1]) / (self.size[1]+0.002)
                                            
        if intersect is None:
            return None
        
        return Intercept(distance = t,
                         point = intersect.point,
                         normal = intersect.normal,
                         texcoords= (u,v),
                         obj = self)

""" class Capsule(Shape):
    def __init__(self, position, radius, height, material):
        self.radius = radius
        self.height = height
        self.normal = ml.normalizeV([0, 1, 0])
        super().__init__(position, material)

    def ray_intersect(self, orig, dir):
        # Primero, verifica si el rayo interseca con las dos semiesferas
        # ubicadas en los extremos de la cápsula.
        
        sphereList = (0, self.height / 2, 0)
        top_sphere = Sphere(ml.addV(self.position, sphereList), self.radius, self.material)
        bottom_sphere = Sphere(ml.substractV(self.position, sphereList), self.radius, self.material)

        top_intersection = top_sphere.ray_intersect(orig, dir)
        bottom_intersection = bottom_sphere.ray_intersect(orig, dir)

        # Calcula la intersección con el cilindro central.
        # Esto se puede hacer calculando la intersección con un cilindro infinito
        # y luego verificando si la intersección está dentro de la altura de la cápsula.
        
        originList = (0, self.height / 2, 0)
        cylinder_origin = ml.substractV(self.position, originList)
        t_cylinder = ml.dotProd((ml.substractV(cylinder_origin, orig)), self.normal) / ml.dotProd(dir, self.normal)
        cylinder_intersection_point = ml.addV(orig, ml.VxE(dir, t_cylinder))

        if (
            cylinder_origin[1] <= cylinder_intersection_point[1] <= (cylinder_origin[1] + self.height)
            and t_cylinder > 0
        ):
            # El rayo intersecta con el cilindro dentro de la altura de la cápsula.
            # Calcula la normal y otros datos necesarios.
            normalC = ml.normalizeV(ml.substractV(cylinder_intersection_point, self.position))
            u = (atan2(normalC[2], normalC[0]) / (2 * pi)) + 0.5
            v = acos(normalC[1]) / pi

            return Intercept(
                distance=t_cylinder,
                point=cylinder_intersection_point,
                normal=normalC,
                texcoords=(u, v),
                obj=self,
            )

        # Compara las intersecciones con las dos semiesferas y devuelve la más cercana.
        if top_intersection and bottom_intersection:
            return top_intersection if top_intersection.distance < bottom_intersection.distance else bottom_intersection
        return top_intersection if top_intersection else bottom_intersection """

#Esfera ovalada     
class Capsule(Shape):
    def __init__(self, position, radius, material, scale=(1, 1, 1)):
        self.radius = radius
        self.scale = scale
        super().__init__(position, material)

    def ray_intersect(self, orig, dir):
        # Aplicar la escala a la dirección del rayo.
        dir = [dir[0] * (1.0 / self.scale[0]), dir[1] * (1.0 / self.scale[1]), dir[2] * (1.0 / self.scale[2])]

        # Transformar el origen del rayo por la escala.
        orig = [orig[0] * self.scale[0], orig[1] * self.scale[1], orig[2] * self.scale[2]]
        
        l = ml.substractV(self.position, orig)
        lengthL = ml.magV(l)
        tca = ml.dotProd(l,dir)
        
        #if radius < d: no hay contacto (False)
        #if radius > d: si hay contacto (True)
        d = (lengthL**2 - tca**2)**0.5
        if d > self.radius:
            return None
        
        thc = (self.radius**2 - d**2)**0.5
        t0 = tca - thc
        t1 = tca + thc
        
        if t0<0:
            t0 = t1
        if t0<0:
            return None
        
        #P = O+D*t0
        p = ml.addV(orig,ml.VxE(dir, t0))
        normal = ml.substractV(p,self.position)
        normal = ml.normalizeV(normal)
        
        u = (atan2(normal[2], normal[0]) / (2*pi)) + 0.5
        v = acos(normal[1]) / pi
        
        return Intercept(distance = t0,
                         point = p,
                         normal = normal,
                         texcoords= (u,v),
                         obj = self)

