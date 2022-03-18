import random
import numpy
class RoomSensor :
    def __init__(self) :
        self.baseMessage = {}
        
    def simulateOddRooms(self,id) :
        self.baseMessage['roomID'] = id
        self.baseMessage['temperature-value'] = random.randint(18,23)
        self.baseMessage['light-value'] = random.randint(0,1)
        self.baseMessage['battery-status'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8])
        return self.baseMessage

    def simulateEvenRooms(self,id) :
        self.baseMessage['roomID'] = id
        self.baseMessage['temperature-value'] =  random.randint(14,20)
        self.baseMessage['light-value'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8])
        self.baseMessage['battery-status'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8])
        return self.baseMessage 

    def emulateData(self,roomID) :
        if roomID % 2 == 0 :
            return self.simulateEvenRooms(roomID)
        else :
            return self.simulateOddRooms(roomID)