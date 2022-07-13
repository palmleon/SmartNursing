import numpy as np

class Fibrillation_Monitor():
    def __init__(self,messagesdict,thresholdsDict):
        # Estrazione messaggi di allarme
        self.__alarm_battery=messagesdict["alarm_battery"].split("{}")
        self.__alarm_place=messagesdict["alarm_place"].split("{}")
        self.__alarm_fibrillation=messagesdict["alarm_fibrillation"].split("{}")
        # Assegnazione soglie
        self.__batteryThreshold = thresholdsDict["battery_threshold"]
        self.__fibrillationState = thresholdsDict["fibrillation_std_threshold"]
        self.__attendabilityThreshold = thresholdsDict["attendability_threshold"]
    
    def fibrillation(self,ID_P,PI,pulse,battery):
        # Suppongo ad esempio, per ogni input, arrivi una lista ogni  10s, con fc=1Hz.
        # Battery, un solo valore

        # battery è la sola tensione di batteria
        if battery<self.__batteryThreshold :# Per informare che il pulsossimetro si sta scaricando (es. suppongo sia scarico a 2.5V)
            alarm=self.__alarm_battery[0]+ID_P+self.__alarm_battery[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro quasi scarico"
            return alarm

        if max(PI)<self.__attendabilityThreshold:
            # Se nessuna lettura attendibile, inutile proseguire
            alarm=self.__alarm_place[0]+ID_P+self.__alarm_place[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            return alarm

        to_remove=[]
        for i in range(len(PI)):
            if PI[i]<self.__attendabilityThreshold:
                # Rimuovo dalla stringa eventuali valori non attendibili
                to_remove.append(i)
        to_remove.sort(reverse=True)
        #print(f"Indici rimossi: {to_remove}")

        for rm in to_remove:
            pulse.pop(rm)
        
        #print(f"Lista pulse ottenuta: {pulse}")

        if len(pulse)<int(len(PI)/2): # Controllo aggiunto in quanto, se vengono rimosse troppe letture, non ha senso valutare la deviazione standard
            alarm=self.__alarm_place[0]+ID_P+self.__alarm_place[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            return alarm
        
        pulse=np.std(pulse)

        if pulse>self.__fibrillationState: # Soglia di deviazione standard che definisce lo stato di fibrillazione
            alarm=self.__alarm_fibrillation[0]+ID_P+self.__alarm_fibrillation[1]
            #return f"ATTENZIONE, il paziente {ID_P} è in un possibile stato di fibrillazione"
            return alarm