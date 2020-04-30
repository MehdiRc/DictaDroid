#!/usr/bin/env python
# coding: utf-8

# In[1]:


#!/usr/bin/env python
# coding: utf-8

from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scatter import Scatter
#from kivy.uix. import
from kivy.uix.label import Label
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.textinput import TextInput
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.progressbar import ProgressBar
from kivy.uix.popup import Popup
from kivy.uix.switch import Switch
from kivy.uix.widget import Widget
from kivy.uix.bubble import Bubble
from kivy.uix.filechooser import FileChooser

from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.factory import Factory
from kivy.properties import ObjectProperty
from kivy.uix.popup import Popup

from  kivy.uix.togglebutton import ToggleButton
from kivy.uix.carousel import Carousel
from kivy.uix.image import AsyncImage
import os

import SoundManager as sm
from kivy.properties import NumericProperty
import kivy.clock

from bisect import bisect

import os
from moviepy.editor import *


# In[2]:


class Engine():
    
    def returntime(self, name):
        return (name.split("_")[2]).split(".")[0]

    def column(self, matrix, i):
        return [row[i] for row in matrix]

    def importPhotos(self, path):
        files = []
        # r=root, d=directories, f = files
        for r, d, f in os.walk(path):
            for file in f:
                files.append((path+"\\"+file,self.returntime(file)))
        return files

    def importPhotos2(self, pictures):
        files = []
        # r=root, d=directories, f = files
        for picPath in pictures:
            parts= picPath.split("\\")
            files.append( (picPath, self.returntime(parts[-1])) )
        return files

    def getAudioLength(self, audiopath):
        audio = AudioFileClip(audiopath)
        audio.reader.close_proc()
        return audio.duration
    
    def stringTotime(self, string):
        h=string[0:2]
        m=string[2:4]
        s=string[4:6]
        return h,m,s 

    def subtime(self, time1,time2):
        h1,m1,s1 = self.stringTotime(time1)
        h2,m2,s2 = self.stringTotime(time2)

        h3= int(h1)-int(h2) 
        m3= int(m1)-int(m2)
        s3= int(s1)-int(s2)

        #print(h1,h2,h3)
        #print(m1,m2,m3)
        #print(s1,s2,s3)
        return s3+60*m3+3600*h3

    def minTime(self, t1,t2):
        h1,m1,s1 = self.stringTotime(t1)
        h2,m2,s2 = self.stringTotime(t2)
        if self.subtime(t1,t2)>0:
            return t2, 1
        else: return t1, 0

    def findFirstPic(self, list):
        minT = "999999"
        firstPos = -999
        for i, pic in enumerate(list):
            minT, p=self.minTime(minT,pic[1])
            if p==1:
                firstPos = i
        return minT, firstPos

    def findabsolutetime(self, piclist):
        timeList =[]
        startTime, s = self.findFirstPic(piclist)
        for pic in piclist:
            timeList.append((pic[0],self.subtime(pic[1],startTime)))
        return timeList

    def findDuration(self, listAbs,audioPath):
        dur=[]
        for i in range(1,len(listAbs)-1):
            dur.append( (listAbs[i][0],listAbs[i][1]-listAbs[i-1][1]))

        t = self.getAudioLength(audioPath)- int(sum(self.column(dur,1)))
        if(t>0):
            dur.append( (listAbs[-1][0], t ) )
        else :
            dur.append( (listAbs[-1][0], 60 ) )
        return dur

    def centerDuration(self, listDur,offrate):
        dur=[]
        dur.append( (listDur[0][0],listDur[0][1]+round(listDur[1][1]/offrate)) )
        for i in range(1,len(listDur)-1):
            d = listDur[i][1]-round(listDur[i][1]/offrate)
            d = d+round(listDur[i+1][1]/offrate)
            dur.append( (listDur[i][0],d) ) 
        dur.append( (listDur[-1][0],listDur[-1][1]-round(listDur[-1][1]/offrate)) )
        return dur
    
    def durationToTime(self, listDur):
        dur = self.column(listDur,1)
        timing =[0]
        for i in range(1,len(dur)):
            timing.append(sum(dur[:i]))
        return timing

    def makevideo2(self, piclist,audiopath,offset):
        if offset < 0 and (piclist[0][1] + offset)>0:
            piclist[0][1]= piclist[0][1] + offset
        elif(offset < 0):
            piclist[0][1]= int(piclist[0][1]/2)+1
        clip = ImageSequenceClip(self.column(piclist, 0),durations=self.column(piclist, 1))

        audio = AudioFileClip(audiopath)
        clip.set_audio(audio.set_duration(clip.duration))

        clip.write_videofile("test3.avi" ,audio=audiopath, fps=1, codec='libx264',audio_codec ='libmp3lame',audio_bitrate='384K')
        clip.close()
        audio.reader.close_proc()
        
    def exportVideo(self, imagesPath,audioPath):
        pictures = self.importPhotos     (imagesPath)
        pics     = self.findabsolutetime (pictures)
        picDur   = self.findDuration     (pics,audioPath)
        picCent  = self.centerDuration   (picDur,3)
        self.makevideo2(picCent,audioPath ,0)


# In[ ]:


eng = Engine()
timings =[]

class FileSelection(FloatLayout):
    
    def init(self):
        global imageDir  
        global soundFile
        global picturesP
        global timings
        timings  =[]
        imageDir = ''
        soundFile= ''
        picturesP= []
                
        
    def gotPathes(self):
        if imageDir  != '' and soundFile != '':
            return True
        else:
            return False

    
    def updateLoadColor(self):
        if self.gotPathes():
            self.ids.load.background_color = [0,1,0,1]
        else:
            self.ids.load.background_color = [1,0,0,1]
    
    def getDir(self, *args): 
        global imageDir 
        global picturesP
        imageDir = self.ids.fc.path
        picturesP = self.ids.fc.files.copy()
        self.ids.text_input_directory.text = str(imageDir)
        self.updateLoadColor()
        
    
    def getFile(self, *args): 
        global soundFile
        try:
            soundFile = self.ids.fc.selection[0]
        except:
            soundFile =''
            
        self.updateLoadColor()  
        self.ids.text_input_file.text = str(soundFile)
    
    
    def load(self):
        global timings
        if self.gotPathes():
            self.parent.ids.caro.loadimages()
            
            pictu   = eng.importPhotos2    (picturesP[1:])
            pics    = eng.findabsolutetime (pictu)
            picDur  = eng.findDuration     (pics,soundFile)
            picCent = eng.centerDuration   (picDur,3)
            timings = eng.durationToTime   (picCent)
            
            print(timings)
            ###
            
            self.parent.initSound(soundFile)
        
class CarouselViewer(BoxLayout):
    
    def loadimages(self):
        global picturesP
        self.ids.imviewer.clear_widgets()
        for pic in picturesP[2:]:
            try:
                image = AsyncImage(source=pic, allow_stretch=True)
                self.ids.imviewer.add_widget(image)
            except: 
                pass
            

    
    def nextImage(self):
        self.ids.imviewer.load_next(mode='next')
    
    def prevImage(self):
        self.ids.imviewer.load_previous()
    
    def showImage(self,n):
        self.ids.imviewer.index = n

        
        
    
    
class Player(BoxLayout):
    sync = True
    filechooser = False 
    fc = FileSelection()
    #/////////////////////////////////////////////////////////////////////////////////////////
    soundM = sm.SoundManager()
    timer = None
    progressBarValue=NumericProperty(0.0)
    #/////////////////////////////////////////////////////////////////////////////////////////
    def filemanager(self, *args):
        if self.filechooser== False:
            self.filechooser= True
            self.fc = FileSelection()
            self.fc.init()
            self.add_widget(self.fc)
        elif self.filechooser== True:
            self.filechooser= False
            self.remove_widget(self.fc)
     #////////////////////////////////////////////////////////////////////////////////////////
     
    def unload(self,*args):
        self.soundM.unloadSound()
        slider = self.ids.slide
        slider.value = 0
        slider.max = 0    
        self.timer.cancel()
        
    def my_callback(self, dt):
        val = self.soundM.getPos()
        self.progressBarValue = val
    
    def initSound(self, sound):
        
        try:
            self.unload()
        except:
            pass
        
        
        try:
            
            son = self.ids.volume
            
            self.soundM.loadSound(sound, son.value)
            
            taille = self.soundM.soundLength()
            slider = self.ids.slide
            slider.max = taille
            
            self.timer = kivy.clock.Clock.schedule_interval(self.my_callback, 0.5)
            self.soundM.sound.bind(on_play=self.startTimer)
            self.soundM.sound.bind(on_stop=self.stopTimer)
            
            self.parent.bind(on_close=self.unload)
        except:
            raise
        
    def stopTimer(self, *args):
        self.timer.cancel()
        slider = self.ids.slide
        val = slider.value
        if (val>=(self.soundM.soundLength()-0.5)):
            self.soundM.currentTime=0
            self.progressBarValue=self.soundM.soundLength()
            
    def startTimer(self, *args):
        self.timer()
     
     
    def playButton(self):
        
        self.soundM.playOrStopSound()
   
    def changeSoundPos(self, val):
        if val-self.progressBarValue > 0.5 or val-self.progressBarValue < -0.5 :
            self.soundM.goTo(val)
        
        if self.sync:
            self.showImageAtTime(val)
        
    def changeSoundValue(self, value):
        self.soundM.setVolume(value)
        
    def showImageAtTime(self,audio_time):
        global timings
        self.ids.caro.showImage( bisect(timings, audio_time)-1)
        
    def nextIm(self):
        self.deactivateSync()
        self.ids.caro.nextImage()
    
    def prevIm(self):
        self.deactivateSync()
        self.ids.caro.prevImage()
    
    def activateSync(self):
        self.sync = True
        self.ids.syncSwitch.active_norm_pos =1
    
    def deactivateSync(self):
        self.sync = False
        self.ids.syncSwitch.active_norm_pos =0
    
    def switchToggle(self,state):
        if state:
            self.activateSync()
        else:
            self.deactivateSync()
    
    
    def goTo(self, val):
        self.soundM.goTo(val)

    def nextSection(self):
        global timings
        self.activateSync()
        if(bisect(timings,self.soundM.getPos())<len(timings)):
            self.goTo(timings[bisect(timings,self.soundM.getPos())])
        
    def prevSection(self):
        global timings
        self.activateSync()
        if(bisect(timings,self.soundM.getPos()-2)>0):
            self.goTo(timings[bisect(timings,self.soundM.getPos())-2])

    #/////////////////////////////////////////////////////////////////////////////////////////
class DictaDroidApp(App):
    def build(self):
        return Player()

if __name__ == "__main__":
    DictaDroidApp().run()


# In[ ]:




