from math import tan, pi, atan2, acos
import mathLib as ml
import random
import pygame
from materials import *
from lights import *

MAX_RECURSION_DEPTH = 3

class Raytracer(object):
    def __init__(self, screen):
        self.screen = screen
        _,_, self.width, self.height = screen.get_rect() #Recibe el rectangulo de la pantalla (_,_, -> x,y)
        
        self.scene = []
        self.lights = []
        
        self.camPosition = [0,0,0]
        
        self.rtViewport(0, 0, self.width, self.height)
        self.rtProyection()
        
        self.rtClearColor(0,0,0)
        self.rtColor(1,1,1)
        self.rtClear()
        
        self.envMap = None
    
    def rtViewport(self,posX, posY, width, height):
        self.vpX = posX
        self.vpY = posY
        self.vpWidth = width
        self.vpHeight = height
    
    def rtProyection(self,fov=60,n=0.1):
        aspectRatio = self.vpWidth/self.vpHeight
        self.nearPlane = n
        self.topEdge = tan((fov*pi/180)/2)*self.nearPlane
        self.rightEdge = self.topEdge * aspectRatio
    
    #Color de fondo    
    def rtClearColor(self, r, g, b):
        #Recibe valores de 0 a 1
        self.clearColor = (r*255,g*255,b*255)
    
    def rtClear(self):
        #Pygame usa valores de colores de 0 a 255
        #Cada color es un Byte
        self.screen.fill((self.clearColor))
    
    #Color por default
    def rtColor(self,r,g,b):
        self.currentColor = (r*255,g*255,b*255)
    
    def rtPoint(self,x,y,color = None):
        y = self.height - y
        
        if (0<=x<self.width) and (0<=y<self.height):
            if color != None:
                color = (int(color[0]*255),
                         int(color[1]*255),
                         int(color[2]*255))
                
                self.screen.set_at((x,y), color)
            else:
                self.screen.set_at((x,y), self.currentColor)
    
    #Generador del rayo
    def rtCastRay(self,orig,dir,sceneObj = None, recursion = 0):
        
        if recursion >= MAX_RECURSION_DEPTH:
            return None
    
        depth = float('inf')
        intercept = None
        hit = None
        
        for obj in self.scene:
            if sceneObj != obj:
                intercept = obj.ray_intersect(orig, dir)
                if intercept != None:
                        
                    if intercept.distance < depth:
                        hit = intercept
                        depth = intercept.distance
        return hit

    def rtRayColor(self, intercept, rayDirection, recursion=0):
        if intercept== None:
            if self.envMap:
                x = (atan2(rayDirection[2], rayDirection[0]) / (2*pi) + 0.5) * self.envMap.get_width() 
                y = acos(rayDirection[1])/pi * self.envMap.get_height()
                
                envColor = self.envMap.get_at((int(x),int(y)))
                
                return [i/255 for i in envColor]
                return
            else:
                return None
        
        #Phong Reflection Model
        #LightColor = AmbientIntensity + DiffuseIntensity + SpecularIntensity
        #FinalColor = SurfaceColor * LightColor
        
        material = intercept.obj.material
        surfaceColor = material.diffuse
        
        if material.texture and intercept.texcoords:
            tx = intercept.texcoords[0]*material.texture.get_width()-1
            ty = intercept.texcoords[1]*material.texture.get_height()-1
            
            texColor = material.texture.get_at((int(tx), int(ty)))
            texColor = [i/255 for i in texColor]
            surfaceColor = [surfaceColor[i]*texColor[i] for i in range(3)]
        
        ambientColor = [0,0,0]
        reflectColor = [0,0,0]
        refractColor = [0,0,0]
        diffuseColor = [0,0,0]
        specularColor = [0,0,0]
        finalColor = [0,0,0]
        
        if material.matType == OPAQUE:
            for light in self.lights:
                if light.lightType == "Ambient":
                    ambientColor = [(ambientColor[i]+light.getLightColor()[i]) for i in range(3)]
                
                else:
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = [(i*-1) for i in light.direction]
                    elif light.lightType == "Point":
                        lightDir = ml.substractV(light.point, intercept.point)
                        lightDir = ml.normalizeV(lightDir)
                        
                    shadowIntersect = self.rtCastRay(intercept.point, lightDir, intercept.obj)
                    
                    if shadowIntersect==None:
                        diffuseColor = [(diffuseColor[i]+light.getDiffuseColor(intercept)[i]) for i in range(3)]
                        specularColor = [(specularColor[i]+light.getSpecularColor(intercept, self.camPosition)[i]) for i in range(3)]
        
        elif material.matType == REFLECTIVE:
            reflect = ml.reflectVector(intercept.normal, [i*-1 for i in rayDirection])
            reflectIntercept = self.rtCastRay(intercept.point, reflect, intercept.obj, recursion + 1)
            reflectColor = self.rtRayColor(reflectIntercept, reflect, recursion + 1)
            
            for light in self.lights:
                if light.lightType != "Ambient":
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = [(i*-1) for i in light.direction]
                    elif light.lightType == "Point":
                        lightDir = ml.substractV(light.point, intercept.point)
                        lightDir = ml.normalizeV(lightDir)
                        
                    shadowIntersect = self.rtCastRay(intercept.point, lightDir, intercept.obj)
                    
                    if shadowIntersect == None:
                        specularColor = [(specularColor[i]+light.getSpecularColor(intercept, self.camPosition)[i]) for i in range(3)]
        
        elif material.matType == TRANSPARENT:
            #Revisar si estoy afuera
            outside = ml.dotProd(rayDirection, intercept.normal) < 0
            
            #Agregar un margen de error
            bias = ml.VxE(intercept.normal, 0.001)
            
            #Generar rayos de reflexion
            reflect = ml.reflectVector(intercept.normal, [i*-1 for i in rayDirection])
            reflectOrigin =  ml.addV(intercept.point, bias) if outside else ml.substractV(intercept.point, bias)
            reflectIntercept = self.rtCastRay(reflectOrigin, reflect, None, recursion + 1)
            reflectColor = self.rtRayColor(reflectIntercept, reflect, recursion+1)
            
            for light in self.lights:
                if light.lightType != "Ambient":
                    lightDir = None
                    if light.lightType == "Directional":
                        lightDir = [(i*-1) for i in light.direction]
                    elif light.lightType == "Point":
                        lightDir = ml.substractV(light.point, intercept.point)
                        lightDir = ml.normalizeV(lightDir)
                        
                    shadowIntersect = self.rtCastRay(intercept.point, lightDir, intercept.obj)
                    
                    if shadowIntersect == None:
                        specularColor = [(specularColor[i]+light.getSpecularColor(intercept, self.camPosition)[i]) for i in range(3)]
            
            #Generar rayos de refraccion si no hay reflexion interna total
            if not totalInternalReflection(intercept.normal, rayDirection, 1.0, material.ior):
                refract = refractVector(intercept.normal, rayDirection, 1.0, material.ior)
                refractOrigin =  ml.substractV(intercept.point, bias) if outside else ml.addV(intercept.point, bias)
                refractIntercept = self.rtCastRay(refractOrigin, refract, None, recursion + 1)
                refractColor = self.rtRayColor(refractIntercept, refract, recursion+1)

                #Usar ecuaciones de Fresnel para determinar la reflexion y refraccion agregar al color final
                kr, kt = fresnel(intercept.normal, rayDirection, 1.0, material.ior)
                reflectColor = ml.VxE(reflectColor, kr)
                refractColor = ml.VxE(refractColor, kt)
            
        lightColor = [(ambientColor[i]+diffuseColor[i]+specularColor[i]+reflectColor[i] + refractColor[i]) for i in range(3)]  
        
        finalColor = [min(1,surfaceColor[i]*lightColor[i])for i in range(3)]
        return finalColor
    
    def rtRender(self):
        indexes = [(i,j) for i in range(self.vpWidth) for j in range(self.vpHeight)]
        random.shuffle(indexes)
        
        for i,j in indexes:
            x = i+self.vpX
            y = j+self.vpY
            if (0<=x<self.width) and (0<=y<self.height):
                #Pasar de coordenadas de ventana a coordenadas NDC (-1 a 1 (coords. normalizadas))
                pX = ((x+0.5-self.vpX)/self.vpWidth)*2-1
                pY = ((y+0.5-self.vpY)/self.vpHeight)*2-1
                
                pX*=self.rightEdge
                pY*=self.topEdge
                
                #Crear un rayo
                direction = (pX,pY,-self.nearPlane)
                direction = ml.normalizeV(direction)
                
                intercept = self.rtCastRay(self.camPosition, direction)
                rayColor = self.rtRayColor(intercept, direction)
                    
                if rayColor != None: 
                    self.rtPoint(x,y,rayColor)
                    pygame.display.flip()
                    