import random
import time
import numpy
class TemperatureAndMotionRoomSensor :
    def __init__(self,baseMessage) :
        self.baseMessage=baseMessage

        
    def simulateOddRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e'][0]['v'] = random.randint(0,1)
        self.baseMessage['e'][1]['v'] = random.randint(24,28)
        self.baseMessage["bt"]=time.time()
        self.baseMessage["bn"]=str(id)+'tmr'
        return self.baseMessage

    def simulateEvenRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e'][0]['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        self.baseMessage['e'][1]['v'] =  random.randint(18,23)
        self.baseMessage["bt"]=time.time()
        self.baseMessage["bn"]=str(id)+'tmr'

        return self.baseMessage 

    def emulateData(self,roomID) :
        if roomID % 2 == 0 :
            return self.simulateEvenRooms(roomID)
        else :
            return self.simulateOddRooms(roomID)