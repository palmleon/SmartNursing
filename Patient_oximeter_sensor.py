from numpy import random

class Temperature_sensor():
    def __init__(self):
        self.__baseMessage={}
    
    def emulate(self,ID_P):
        # Una lista di 10 valori ogni 10 secondi di PI, saturazione e battiti (associati ad un solo valore di batteria)
        if ID_P==1:
            # Paziente sano con batteria di buon livello
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]=random.uniform(low=4,high=20,size=10)
            self.__baseMessage["ox"]=random.uniform(low=96,high=99,size=10)
            self.__baseMessage["pulse"]=random.uniform(low=70,high=72,size=10)
        if ID_P==2:
            # Paziente sano con batteria scarica
            self.__baseMessage["battery-value"]=random.uniform(low=2.78,high=2.79)
            self.__baseMessage["PI"]=random.uniform(low=4,high=20,size=10)
            self.__baseMessage["ox"]=random.uniform(low=96,high=99,size=10)
            self.__baseMessage["pulse"]=random.uniform(low=70,high=72,size=10)

