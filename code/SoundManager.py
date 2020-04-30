# -*- coding: utf-8 -*-
"""
Created on Wed Jul 31 17:49:26 2019

@author: pierre
"""
import sys

from kivy.core.audio import SoundLoader




class SoundManager:
    
    
    
    def __init__(self): # je pourrais faire passer le loading dans le constructeur
    
        self.sound = None
        self.currentTime = 0
        self.isStop = 1
        
    def getSound(self):
        return self.sound
    
    def getPos(self):
        
        if self.isStop:
            return self.currentTime
        else:
            return self.sound.get_pos()
    
    def loadSound(self, *args):#rajouter une secu, annalyser avec sys si le fichier existe vraiment
        
        try:
            self.sound = SoundLoader.load(args[0])
            self.sound.volume=args[1]
            if self.sound:
                print("Sound found at %s" % self.sound.source)
                print("Sound is %.3f seconds" % self.sound.length)
        except:
            print("Unexpected error:", sys.exc_info()[0])
            raise
            
    
    def unloadSound(self):
        
        if self.sound:
            self.sound.unload()
            self.sound = None
            self.currentTime = 0.0
    
    def playSound(self): #a revoir ici setvolume inutile
        
        if self.sound:
            self.sound.play()
        
    def playOrStopSound(self):
        
        if self.sound:
            if self.sound.state == "play":
                self.currentTime = self.sound.get_pos()
                self.isStop=1
                self.sound.stop()
            else:
                self.isStop=0
                self.sound.play()
                self.sound.seek(self.currentTime)
                
    def setVolume(self, val):
        
        if self.sound:
            if(0<=val<=1):
                self.sound.volume= val
            else:
                raise ValueError("sound value outside bound [0,1]: {0}".format(val))
            
    def backToStart(self):
        
        if self.sound:
            self.currentTime=0
            self.sound.seek(0)
            
    def goToEnd(self):
        if self.sound:
            self.currentTime = self.sound.length
            self.sound.seek(self.sound.length)
            
    def goTo(self, pos):
        
        if self.sound:
            if(0<=pos<=self.sound.length):
                self.currentTime=pos
                self.sound.seek(pos)
            else:
                raise ValueError("position value outside bound [0,{0}]: {1}".format(self.sound.length,pos))
                
                
                
    def soundLength(self):
        
        if self.sound:
            
            try:
                res = self.sound.length
                return res
            except:
                raise
                
        else:
            return 0
            
        
        
        
        
        
        
        
        
        
        