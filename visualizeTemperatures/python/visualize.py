# -*- coding: utf-8 -*-
"""
Created on Sun Aug 30 15:29:11 2015

@author: whho
"""

'''
Show all different interpolation methods for imshow
'''
import csv
import numpy as np
from matplotlib import pyplot as plt
from matplotlib import animation
import scipy.misc as misc
import serial
import StringIO

class CSVData:
    def __init__(self):
        self.data = []
        self.i = 0;
        with open('evb90620log.csv','rb') as csvfile:
            reader = csv.reader(csvfile, delimiter=',')
            for r in reader:
                row = [(40+float(x))/40 for x in r[2:66]]
                self.data.append(row)

    def next(self):
        if(self.i<len(self.data)):
            d = self.data[self.i]
            self.i += 1
            return d
        else:
            return self.data[self.i-1];
                
    def getCSVImg(self):
        l = self.next()
        a = np.array(l)
        try:
            a = a.reshape(16,4).transpose()
        except ValueError:
            print a;
        return misc.imresize(a,(self.ny,self.nx),interp='cubic')
        #return a
                
class SerialData:
    def __init__(self):
        self.ser = serial.Serial('COM28',115200,timeout=3)
        self.ser.flushInput();

    def __iter__(self):
        return self

    def next(self):
        if self.ser.closed == True:
            self.ser.open();    
        line = self.ser.readline()
        row = [0 for i in range(64)]
        if len(line) > 0:
            it = StringIO.StringIO(line)
            rdr = csv.reader(it)
            for r in rdr:                  
                if len(r) == 64:
                    try:
                        row = [float(c) for c in r]                        
                    except ValueError:
                        print "Value Error"
        return self.row2img(row);
        
    def close(self):
        self.ser.close();        
        
    @staticmethod              
    def row2img(row):
        ny = 4*4
        nx = ny * 4        
        a = np.array(row)
        try:
            a = a.reshape(16,4).transpose()
        except ValueError:
            print "ValueError:"
            print a;
        #a = self.normalize(a)
        #a = misc.imresize(a,(ny,nx),interp='cubic')        
        #print a;
        return a;                    

class Animator:
    ny = 8
    nx = ny * 4
    def __init__(self):
        self.serdata = SerialData();
        self.fig = plt.figure()

    def getRandImg(self):
        return  np.random.rand(self.ny, self.nx)
        
    def normalize(self, v):
        m=np.max(np.abs(v))
        if m==0: 
           return v
        print v/m   
        return v/m
        
    def doAnimation(self):    
        #data = np.zeros((nx, ny))
        #cmap = 'gist_gray';
        #cmap = 'gist_heat';
        cmap = 'hot';
        #cmap = 'gist_rainbow_r';
        
        #interpolation='bilinear'
        #interpolation='lanczos'        
        #self.im = plt.imshow(self.getCSVImg(), interpolation=interpolation, cmap=cmap, vmin=0, vmax=1)
        self.im = plt.imshow(self.serdata.next(), interpolation='none', cmap=cmap, vmin=60, vmax=150)
        plt.colorbar();
        
        def init():
            self.im.set_data(np.zeros((self.nx, self.ny)))
        
        def animate(i):
            #img = self.getSerialImg()
            #self.im.set_data(img)            
            self.im.set_data(i)

        self.funcanim = animation.FuncAnimation(self.fig, animate, init_func=init, 
                                            frames=self.serdata,
                                            interval=31)

    def stopAnimation(self):
        self.serdata.close();        

    def onClick(self, event):
        self.stopAnimation()
        del self
                                
if __name__ == '__main__':
    anim = Animator()

    
    anim.fig.canvas.mpl_connect('close_event', anim.onClick)

    anim.doAnimation()
    #while(1):
    #    print a.getSerialImg()
    print 'Done'                       
    #sd = SerialData()
    #sd.next()