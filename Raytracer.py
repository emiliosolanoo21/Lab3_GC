import pygame
from pygame.locals import * 
from rt import Raytracer
from figures import *
from lights import *
from materials import *

width = 512
height = 512

pygame.init()

screen = pygame.display.set_mode((width,height), pygame.DOUBLEBUF | pygame.HWACCEL | pygame.HWSURFACE | pygame.SCALED)
screen.set_alpha(None)

raytracer = Raytracer(screen)

#Se puede usar cualquier formato de imagen.
#hdri-hub.com
raytracer.envMap = pygame.image.load("images/day.jpg")
raytracer.rtClearColor(0.25,0.25,0.25)

#Carga de texturas
ballTexture = pygame.image.load("images/Jabulani.jpg")
flowTexture = pygame.image.load("images/flow.jpg")
rubixTexture = pygame.image.load("images/rubix.jpg")

#Carga de materiales
rugbyBall = Material(texture = ballTexture, spec = 20, ks = 0.01)
reflectFlow = Material(texture = flowTexture, spec = 64, ks = 0.1, matType= REFLECTIVE)
rubix = Material(texture = rubixTexture, spec = 64, ks = 0.1, matType= TRANSPARENT)



#Colocacion de plano base
#raytracer.scene.append(Plane(position=(0,-2,0), normal = (0,1,-0.02), material = c1))

#Colocacion de cápsulas
raytracer.scene.append(Ellipsoid(position = (-1.2,-1,-5), radii = (1, 1.5, 0.2), material = rubix))
raytracer.scene.append(Ellipsoid(position = (1,1.5,-5), radii = (1.35, 0.6, 1.5), material = rugbyBall))
raytracer.scene.append(Ellipsoid(position = (0,-0.5,-10), radii = (1.25,2,1), material = reflectFlow))



#iluminacion minima del ambiente
raytracer.lights.append(AmbientLight(intensity=0.3))
raytracer.lights.append(DirectionalLight(direction=(1,1,-2), intensity=0.95))

#No colocar en la misma ubicacion que ninguna figura
#raytracer.lights.append(PointLight(point=(0,2,-5), intensity=10, color= (1,1,1)))

raytracer.rtClear()
raytracer.rtRender()

print("\nTiempo de renderizado:", pygame.time.get_ticks() / 1000, "segundos")

isRunning = True
while isRunning:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            isRunning = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                isRunning=False

rect = pygame.Rect(0,0,width,height)
sub = screen.subsurface(rect)
pygame.image.save(sub, "result.jpg")
                
pygame.quit()           