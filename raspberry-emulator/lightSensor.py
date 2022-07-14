import random
import numpy
class LightSensor :
    def __init__(self) :
        self.baseMessage={"bn" : "","bt":0,"e" : {"n":"light","u":"bool","v":0}}

        
    def simulateOddRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e']['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        return self.baseMessage

    def simulateEvenRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e']['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        return self.baseMessage 

    def emulateData(self,roomID) :
        if roomID % 2 == 0 :
            return self.simulateEvenRooms(roomID)
        else :
            return self.simulateOddRooms(roomID)