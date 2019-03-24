#!/usr/bin/python2
# -*- coding: utf-8-*-
import game, settings, pygame
conf = settings.Settings()
if not conf.load():
    print "Couldn't load settings, using defaults instead."  
pygame.init()
pygame.display.set_mode((640, 480), pygame.DOUBLEBUF | pygame.OPENGL | pygame.RESIZABLE)
pygame.display.set_caption("4DeBlock")
game.main(conf, 2)
