from numpy import random
import time

class Oximeter_sensor():
    def __init__(self,baseMessage,sampleNumber):
        
        self.__baseMessage=baseMessage
        self.__sampleNumber = sampleNumber
    
    def emulate(self,ID_P):
        # Una  lista di self.__sampleNumber valori ogni self.__sampleNumber secondi di PI, saturazione e battiti (associati ad un solo valore di batteria)
        if ID_P==1:
            # Paziente sano con batteria di buon livello
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=96,high=100,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=70,high=74,size= self.__sampleNumber).tolist())
        elif ID_P==2:
            # Paziente sano con batteria scarica
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.78,high=2.79)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=96,high=100,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=70,high=74,size= self.__sampleNumber).tolist())
        elif ID_P==3:
            # Paziente con pulsossimetro tolto
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=0,high=4,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=96,high=100,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=70,high=74,size= self.__sampleNumber).tolist())
        elif ID_P==4:
            # Paziente con pulsossimetro messo male (solo per fibrillation)
            first_sample = int(self.__sampleNumber/2)+1
            restant_sample = self.__sampleNumber-first_sample
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=0,high=4,size=first_sample).tolist()+random.uniform(low=4,high=20,size=restant_sample).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=96,high=100,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=70,high=74,size= self.__sampleNumber).tolist())
        elif ID_P==5:
            # Paziente con saturazione bassa
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=90,high=95,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=70,high=74,size= self.__sampleNumber).tolist())
        elif ID_P==6:
            # Paziente con battito cardiaco basso
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=96,high=100,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=50,high=55,size= self.__sampleNumber).tolist())
        elif ID_P==7:
            # Paziente con battito cardiaco alto
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=96,high=100,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=100,high=104,size= self.__sampleNumber).tolist())
        elif ID_P==8:
            # Paziente in fibrillazione
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=96,high=100,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=70,high=90,size= self.__sampleNumber).tolist())
        elif ID_P==9:
            # Paziente combinato saturazione bassa e battito alto
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=90,high=95,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=100,high=104,size= self.__sampleNumber).tolist())
        else:
            # Paziente combinato saturazione bassa e battito basso
            self.__baseMessage["e"][0]["v"]=random.uniform(low=2.81,high=3.0)
            self.__baseMessage["e"][1]["v"]= (random.uniform(low=4,high=20,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][2]["v"]= (random.randint(low=90,high=95,size= self.__sampleNumber).tolist())
            self.__baseMessage["e"][3]["v"]= (random.randint(low=50,high=55,size= self.__sampleNumber).tolist())

        self.__baseMessage["bn"]=str(ID_P)+'o'
        self.__baseMessage["bt"]=time.time()
        
        return self.__baseMessage