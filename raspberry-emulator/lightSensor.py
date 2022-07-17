import random
import numpy
import time

class LightSensor :
    def __init__(self,baseMessage) :
        self.__baseMessage=baseMessage

        
    def simulateOddRooms(self,id) :
        #self.baseMessage['roomID'] = id
        self.__baseMessage['e']['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.2, 0.8]).item()
        self.__baseMessage['bn']=str(id)+'l'
        self.__baseMessage["bt"]=time.time()
        return self.__baseMessage

    def simulateEvenRooms(self,id) :
        #self.__baseMessage['roomID'] = id
        self.__baseMessage['e']['v'] = numpy.random.choice(numpy.arange(0,2), p=[0.8, 0.2]).item()
        self.__baseMessage['bn']=str(id)+'l'
        self.__baseMessage["bt"]=time.time()
        return self.__baseMessage 

    def emulateData(self,roomID) :
        if roomID % 2 == 0 :
            return self.simulateEvenRooms(roomID)
        else :
            return self.simulateOddRooms(roomID)