import numpy as np

class Fibrillation_Monitor():
    def __init__(self,messagesdict):
        # Estrazione messaggi di allarme
        self.__alarm_battery=messagesdict["alarm_battery"].split("{}")
        self.__alarm_place=messagesdict["alarm_place"].split("{}")
        self.__alarm_fibrillation=messagesdict["alarm_fibrillation"].split("{}")
    
    def fibrillation(self,ID_P,PI,pulse,battery):
        # Suppongo, per ogni input, arrivi una lista ogni  10s, con fc=1Hz.
        # Battery, un solo valore ogni 10s

        
        # battery è la sola tensione di batteria
        if battery<2.8:# Per informare che il pulsossimetro si sta scaricando (es. suppongo sia scarico a 2.5V)
            alarm=self.__alarm_battery[0]+ID_P+self.__alarm_battery[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro quasi scarico"
            return alarm

        if max(PI)<4: # Cercando su internet, la soglia per una lettura attendibile è al 4%
            # Se nessuna lettura attendibile, inutile proseguire
            alarm=self.__alarm_place[0]+ID_P+self.__alarm_place[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            return alarm

        to_remove=[]
        for i in range(len(PI)):
            if PI[i]<4:
                # Rimuovo dalla stringa eventuali valori non attendibili
                to_remove.append(i)
        to_remove.sort(reverse=True)
        print(f"Indici rimossi: {to_remove}")

        for rm in to_remove:
            pulse.pop(rm)
        
        # Solo per test, da cancellare quando finito
        print(f"Lista pulse ottenuta: {pulse}")


        if len(pulse)<5: # Controllo aggiunto in quanto, se vengono rimosse troppe letture, non ha senso valutare la deviazione standard
            alarm=self.__alarm_place[0]+ID_P+self.__alarm_place[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            return alarm
        
        pulse=np.std(pulse)

        if pulse>5: # Soglia di deviazione standard che definische lo stato di fibrillazione
            alarm=self.__alarm_fibrillation[0]+ID_P+self.__alarm_fibrillation[1]
            #return f"ATTENZIONE, il paziente {ID_P} è in un possibile stato di fibrillazione"
            return alarm