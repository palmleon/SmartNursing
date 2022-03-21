from numpy import random

class Oximeter_sensor():
    def __init__(self):
        self.__baseMessage={}
    
    def emulate(self,ID_P):
        # Una  lista di 10 valori ogni 10 secondi di PI, saturazione e battiti (associati ad un solo valore di batteria)
        if ID_P==1:
            # Paziente sano con batteria di buon livello
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=4,high=20,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=96,high=100,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=70,high=74,size= 10).tolist())
        elif ID_P==2:
            # Paziente sano con batteria scarica
            self.__baseMessage["battery-value"]=random.uniform(low=2.78,high=2.79)
            self.__baseMessage["PI"]= (random.uniform(low=4,high=20,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=96,high=100,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=70,high=74,size= 10).tolist())
        elif ID_P==3:
            # Paziente con pulsossimetro tolto
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=0,high=4,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=96,high=100,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=70,high=74,size= 10).tolist())
        elif ID_P==4:
            # Paziente con pulsossimetro messo male (solo per fibrillation)
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=0,high=4,size=6)+random.uniform(low=4,high=20,size=4))
            self.__baseMessage["ox"]= (random.randint(low=96,high=100,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=70,high=74,size= 10).tolist())
        elif ID_P==5:
            # Paziente con saturazione bassa
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=4,high=20,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=93,high=95,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=70,high=74,size= 10).tolist())
        elif ID_P==6:
            # Paziente con battito cardiaco basso
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=4,high=20,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=96,high=100,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=50,high=55,size= 10).tolist())
        elif ID_P==7:
            # Paziente con battito cardiaco alto
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=4,high=20,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=96,high=100,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=100,high=104,size= 10).tolist())
        elif ID_P==8:
            # Paziente in fibrillazione
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=4,high=20,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=96,high=100,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=70,high=90,size= 10).tolist())
        else:
            # Paziente combinato saturazione bassa e battito alto
            self.__baseMessage["battery-value"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["PI"]= (random.uniform(low=4,high=20,size= 10).tolist())
            self.__baseMessage["ox"]= (random.randint(low=93,high=95,size= 10).tolist())
            self.__baseMessage["pulse"]= (random.randint(low=100,high=104,size= 10).tolist())

        self.__baseMessage["patientID"]=ID_P
        return self.__baseMessage