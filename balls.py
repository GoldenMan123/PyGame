#!/usr/bin/env python
# coding: utf

import pygame
import random
import math

SIZE = 640, 480

def intn(*arg):
    return map(int,arg)

def Init(sz):
    '''Turn PyGame on'''
    global screen, screenrect
    pygame.init()
    screen = pygame.display.set_mode(sz)
    screenrect = screen.get_rect()

class GameMode:
    '''Basic game mode class'''
    def __init__(self):
        self.background = pygame.Color("black")

    def Events(self,event):
        '''Event parser'''
        pass

    def Draw(self, screen):
        screen.fill(self.background)

    def Logic(self, screen):
        '''What to calculate'''
        pass

    def Leave(self):
        '''What to do when leaving this mode'''
        pass

    def Init(self):
        '''What to do when entering this mode'''
        pass

class Ball:
    '''Simple ball class'''

    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0)):
        '''Create a ball from image'''
        self.fname = filename
        self.surface = pygame.image.load(filename)
        self.rect = self.surface.get_rect()
        self.speed = speed
        self.pos = pos
        self.newpos = pos
        self.active = True

    def draw(self, surface):
        surface.blit(self.surface, self.rect)

    def gravity(self, t):
        self.speed = self.speed[0], self.speed[1] + 0.2 * t

    def action(self):
        '''Proceed some action'''
        if self.active:
            self.gravity(0.5)
            self.pos = self.pos[0]+self.speed[0], self.pos[1]+self.speed[1]
            self.gravity(0.5)

    def logic(self, surface):
        gravity = 0.2
        x,y = self.pos
        dx, dy = self.speed
        if x < self.rect.width/2:
            x = self.rect.width/2
            dx = -dx
        elif x > surface.get_width() - self.rect.width/2:
            x = surface.get_width() - self.rect.width/2
            dx = -dx
        if y < self.rect.height/2:
            dh = self.rect.height / 2 - y
            dy = -dy
            dy = math.sqrt(2 * 0.2 * dh + dy ** 2)
            y = self.rect.height/2
        elif y > surface.get_height() - self.rect.height/2:
            dh = y - surface.get_height() + self.rect.height / 2
            dy = -dy
            de = -2 * 0.2 * dh + dy ** 2
            if de > 0:
                dy = -math.sqrt(de)
            y = surface.get_height() - self.rect.height/2
        self.pos = x,y
        self.speed = dx,dy
        self.rect.center = intn(*self.pos)

class RotatingBall(Ball):
    
    def __init__(self, filename, pos = (0.0, 0.0), speed = (0.0, 0.0), size = 1.0, angle_speed = 0.0):
        Ball.__init__(self, filename, pos, speed)
        self.size = size
        self.angle_speed = angle_speed
        self.angle = 0.0
        self.rect = pygame.transform.rotozoom(self.surface, self.angle, self.size).get_rect()

    def draw(self, surface):
        sfc = pygame.transform.rotozoom(self.surface, self.angle, self.size)
        rct = sfc.get_rect()
        rct.center = self.rect.center
        surface.blit(sfc, rct)

    def action(self):
        Ball.action(self)
        self.angle += self.angle_speed

class Universe:
    '''Game universe'''

    def __init__(self, msec, tickevent = pygame.USEREVENT):
        '''Run a universe with msec tick'''
        self.msec = msec
        self.tickevent = tickevent

    def Start(self):
        '''Start running'''
        pygame.time.set_timer(self.tickevent, self.msec)

    def Finish(self):
        '''Shut down an universe'''
        pygame.time.set_timer(self.tickevent, 0)

class GameWithObjects(GameMode):

    def __init__(self, objects=[]):
        GameMode.__init__(self)
        self.objects = objects

    def locate(self, pos):
        return [obj for obj in self.objects if obj.rect.collidepoint(pos)]

    def Events(self, event):
        GameMode.Events(self, event)
        if event.type == Game.tickevent:
            for obj in self.objects:
                obj.action()

    def Logic(self, surface):
        GameMode.Logic(self, surface)
        for obj in self.objects:
            obj.logic(surface)

    def Draw(self, surface):
        GameMode.Draw(self, surface)
        for obj in self.objects:
            obj.draw(surface)

class GameWithDnD(GameWithObjects):

    def __init__(self, *argp, **argn):
        GameWithObjects.__init__(self, *argp, **argn)
        self.oldpos = 0,0
        self.drag = None

    def Events(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            click = self.locate(event.pos)
            if click:
                self.drag = click[0]
                self.drag.active = False
                self.oldpos = event.pos
        elif event.type == pygame.MOUSEMOTION and event.buttons[0]:
                if self.drag:
                    self.drag.pos = event.pos
                    self.drag.speed = event.rel
        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if self.drag:
                self.drag.active = True
                self.drag = None
        GameWithObjects.Events(self, event)

Init(SIZE)
Game = Universe(10)

Run = GameWithDnD()
for i in xrange(2):
    x, y = random.randrange(screenrect.w), random.randrange(screenrect.h)
    dx, dy = 1+random.random()*5, 1+random.random()*5
    sz = random.random() / 2.0 + 0.5
    dphi = 10 * (random.random() - 0.5)
    Run.objects.append(RotatingBall("ball.gif",(x,y),(dx,dy), sz, dphi))

Game.Start()
Run.Init()
again = True
while again:
    event = pygame.event.wait()
    if event.type == pygame.QUIT:
        again = False
    Run.Events(event)
    Run.Logic(screen)
    Run.Draw(screen)
    pygame.display.flip()
Game.Finish()
pygame.quit()
