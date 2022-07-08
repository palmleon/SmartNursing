from numpy import random
import time

class Temperature_sensor():
    def __init__(self):
        self.__baseMessage={"bn" : "","bt":0,"e" : [{"n":"battery","u":"V","v":0}, {"n":"temperature","u":"cel","v":0}]}
    
    def emulate(self,ID_P):
        # 1 dato di batteria e temperatura insieme ogni 30 secondi
        if ID_P==1:
            # Paziente sano con batteria di buon livello
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]=random.uniform(low=36.45,high=36.55)
        elif ID_P==2:
            # Paziente sano con batteria scarica
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.77,high=2.79)
            self.__baseMessage["e"][1]["v"]=random.uniform(low=36.45,high=36.55)
        elif ID_P==3:
            # Paziente con termometro spostato e con batteria carica (non faccio entrambi i casi, in quanto l'analizzatore si ferma prima mandando solo batteria scarica)
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]=random.uniform(low=34,high=35)
        else:
            # Paziente con febbre e con batteria carica
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]=random.uniform(low=37.1,high=37.5)
        
        #self.__baseMessage["bn"]=ID_P
        self.__baseMessage["bt"]=time.time()
        return self.__baseMessage