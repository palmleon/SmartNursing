from numpy import random

class Temperature_sensor():
    def __init__(self):
        self.__baseMessage={}
    
    def emulateData(self,ID_P):
        # 1 dato di batteria e temperatura insieme ogni 30 secondi
        if ID_P%2==0:
            # Paziente sano con batteria di buon livello
            self.__baseMessage["patientID"] = ID_P
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["temperature-value"]=random.uniform(low=36.45,high=36.55)
            return self.__baseMessage
        elif ID_P%3==0:
            # Paziente sano con batteria scarica
            self.__baseMessage["patientID"] = ID_P
            self.__baseMessage["battery-value"]=random.uniform(low=2.79,high=2.8)
            self.__baseMessage["temperature-value"]=random.uniform(low=36.45,high=36.55)
            return self.__baseMessage
        elif ID_P%5==0:
            # Paziente con termometro spostato e con batteria carica (non faccio entrambi i casi, in quanto l'analizzatore si ferma prima mandando solo batteria scarica)
            self.__baseMessage["patientID"] = ID_P
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["temperature-value"]=random.uniform(low=34,high=35)
            return self.__baseMessage
        else:
            # Paziente con febbre e con batteria carica
            self.__baseMessage["patientID"] = ID_P
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["temperature-value"]=random.uniform(low=37.1,high=38)
            return self.__baseMessage