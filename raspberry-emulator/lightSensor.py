import random
import numpy
import time

class LightSensor :
    def __init__(self,baseMessage) :
        self.baseMessage=baseMessage

        
    def simulateOddRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e']['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        self.baseMessage['bn']=str(id)+'l'
        self.baseMessage["bt"]=time.time()
        return self.baseMessage

    def simulateEvenRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e']['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        self.baseMessage['bn']=str(id)+'l'
        self.baseMessage["bt"]=time.time()
        return self.baseMessage 

    def emulateData(self,roomID) :
        if roomID % 2 == 0 :
            return self.simulateEvenRooms(roomID)
        else :
            return self.simulateOddRooms(roomID)