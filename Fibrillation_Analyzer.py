import numpy as np

class Fibrillation_Monitor():
    def __init__(self,ID_P,ID_pulse):
        self.__ID_P=ID_P
        self.__ID_Pulse=ID_pulse
    
    def fibrillation(self,PI,pulse,battery):
        # Suppongo, per ogni input, arrivi una stringa ogni  10s, con fc=1Hz.
        # Battery, potrebbe essere anche un solo valore ogni 10s(discorso di ridurre i bit mandati)
        
        # battery è la sola tensione di batteria
        if battery<2.8:# Per informare che il pulsossimetro si sta scaricando (es. suppongo sia scarico a 2.5V)
            #return f"ATTENZIONE, il paziente {self.__ID_P} ha il pulsossimetro quasi scarico"
            return [5, self.__ID_P]

        if max(PI)<4: # Cercando su internet, la soglia per una lettura attendibile è al 4%
            # Se nessuna lettura attendibile, inutile proseguire
            return f"ATTENZIONE, il paziente {self.__ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            #return [6, self.__ID_P]

        to_remove=[]
        for i in range(PI):
            if PI[i]<4:
                # Rimuovo dalla stringa eventuali valori non attendibili
                to_remove.append(i)
        to_remove.sort(reverse=True)
        for rm in to_remove:
            pulse.pop(rm)
        
        if len(pulse)<5: # Controllo aggiunto in quanto, se vengono rimosse troppe letture, non ha senso valutare la deviazione standard
            return f"ATTENZIONE, il paziente {self.__ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
        
        pulse=np.std(pulse)

        if pulse >0.1: # VALORE SOGLIA MESSO A CASO
            return f"ATTENZIONE, il paziente {self.__ID_P} è in un possibile stato di fibrillazione"