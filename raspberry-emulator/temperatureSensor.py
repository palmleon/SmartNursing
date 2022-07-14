import random
import numpy
class TemperatureRoomSensor :
    def __init__(self) :
        self.baseMessage={"bn" : "","bt":0,"e" : [{"n":"presence","u":"bool","v":0},{"n":"temperature","u":"cel","v":0}]}

        
    def simulateOddRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e'][0]['v'] = random.randint(0,1)
        self.baseMessage['e'][1]['v'] = random.randint(24,28)
        return self.baseMessage

    def simulateEvenRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.baseMessage['e'][0]['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        self.baseMessage['e'][1]['v'] =  random.randint(18,23)
        return self.baseMessage 

    def emulateData(self,roomID) :
        if roomID % 2 == 0 :
            return self.simulateEvenRooms(roomID)
        else :
            return self.simulateOddRooms(roomID)