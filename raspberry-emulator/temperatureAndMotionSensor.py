import random
import time
import numpy
class TemperatureAndMotionRoomSensor :
    def __init__(self,baseMessage) :
        self.__baseMessage=baseMessage

        
    def simulateOddRooms(self,id) :
        #self.__baseMessage['roomID'] = id
        self.__baseMessage['e'][0]['v'] = random.randint(0,1)
        self.__baseMessage['e'][1]['v'] = random.randint(24,28)
        self.__baseMessage["bt"]=time.time()
        self.__baseMessage["bn"]=str(id)+'tmr'
        return self.__baseMessage

    def simulateEvenRooms(self,id) :
        #self.__baseMessage['roomID'] = id
        self.__baseMessage['e'][0]['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        self.__baseMessage['e'][1]['v'] =  random.randint(18,23)
        self.__baseMessage["bt"]=time.time()
        self.__baseMessage["bn"]=str(id)+'tmr'

        return self.__baseMessage 

    def emulateData(self,roomID) :
        if roomID % 2 == 0 :
            return self.simulateEvenRooms(roomID)
        else :
            return self.simulateOddRooms(roomID)