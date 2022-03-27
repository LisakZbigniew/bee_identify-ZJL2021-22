import numpy as np
import copy
from pathlib import Path
import pickle
import cv2

class Photo():
    @classmethod
    def create(cls,path):
        data = np.load(path,allow_pickle=True)
        if((not 'colorimg' in data or data['colorimg'] is None) and data['img'] is None):
            return None
        return cls(data)


    def __init__(self,data):
        self.photo_data = data
        self.start_point = (-1,-1)
        self.end_point = (-1,-1)
        if((not 'colorimg' in self.photo_data or self.photo_data['colorimg'] is None) and self.photo_data['img'] is None):
            self = None
            return
        self.noColor = False
        if(not 'colorimg' in self.photo_data or self.photo_data['colorimg'] is None):
            self.noColor = True
            self.photo_data['colorimg'] = cv2.cvtColor(self.photo_data['img'], cv2.COLOR_BAYER_RG2BGR)
        shape = self.photo_data['colorimg'].shape
        self.height, self.width, _ = shape
        self.center = (self.width/2,self.height/2)
        self.zoom = 1.0

    def getCurrentlyVisibleCords(self):
        visWidth = self.width / self.zoom
        visHeight = self.height / self.zoom

        x0 = min(max(self.center[0] - visWidth/2,0),self.width - visWidth)
        x1 = x0 + visWidth

        y0 = min(max(self.center[1] - visHeight/2,0),self.height - visHeight)
        y1 = y0 + visHeight
        return int(x0),int(y0),int(x1),int(y1)
    
    def getVisibleImage(self):
        left,up,right,down = self.getCurrentlyVisibleCords()
        return self.photo_data['colorimg'][up:down,left:right]*4

    def resetZoom(self):
        self.center = (self.width/2,self.height/2)
        self.zoom = 1.0
    
    def setCenter(self,x,y):
        left,up,_,_ = self.getCurrentlyVisibleCords()
        self.center = (left+x,up+y)

    def mark(self,x,y):
        left,up,_,_ = self.getCurrentlyVisibleCords()
        point = (left+x,up+y)
        if(self.start_point == (-1,-1)):
            self.start_point = point
        else:
            self.end_point = point

    def isVisible(self,point):
        (x,y) = point
        #print(point)
        left,up,right,down = self.getCurrentlyVisibleCords()
        #print(self.getCurrentlyVisibleCords())
        if(x>=left and x<=right and y>=up and y<=down):
            return True
        return False

    def isVisible(self,point):
        left,up,right,down = self.getCurrentlyVisibleCords()
        (x,y) = point
        if(x>=left and x<=right and y>=up and y<=down):
            return (x-left,y-up)
        return None

    def getVisibleStart(self):
        return self.isVisible(self.start_point)

    def getVisibleEnd(self):
        return self.isVisible(self.end_point)
    
    def getSamples(self,num):
        if(self.start_point == (-1,-1) or self.end_point == (-1,-1)):
            return []
        diff = (self.end_point[0]-self.start_point[0],self.end_point[1]-self.start_point[1])
        #print(diff)
        step = (diff[0]/(num-1),diff[1]/(num-1))
        #print(step)
        points = [(int(self.start_point[0] + step[0]*i),int(self.start_point[1] + step[1]*i)) for i in range(0,num)]
        #print(points)
        return points

    def getCurrentlyVisibleSamples(self,num):
        return filter((lambda x : x != None),map(self.isVisible,self.getSamples(num)))

    def saveSamples(self,num,size,names):
        points = self.getSamples(num)
        sample = copy.deepcopy(self.photo_data)
        size = int((size-1)/2)
        dir = '.\samples'

        if(not Path(dir).exists()):
            Path(dir).mkdir()

        photo_type = 'colorimg'
        if(self.noColor):
            sample.pop('colorimg')
            photo_type = 'img'

        for i,point in enumerate(points):
            sample[photo_type] = self.photo_data[photo_type][point[1]-size:point[1]+size+1,point[0]-size:point[0]+size+1]
            sample['start'] = (point[1]-size,point[0]-size)
            label = names[i] if len(names) > i else str(i)
            sample['filename'] = self.photo_data['filename'][0:-3:1] + "_" + label + '.np'
            pickle.dump(sample,Path(dir+"\\"+sample['filename'].replace(':','%')).open('wb'))




        