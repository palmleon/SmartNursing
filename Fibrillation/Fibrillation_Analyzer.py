import numpy as np

class Fibrillation_Monitor():
    def __init__(self):
        pass
    
    def fibrillation(self,ID_P,PI,pulse,battery):
        # Suppongo, per ogni input, arrivi una stringa ogni  10s, con fc=1Hz.
        # Battery, potrebbe essere anche un solo valore ogni 10s(discorso di ridurre i bit mandati)
        
        # battery è la sola tensione di batteria
        if battery<2.8:# Per informare che il pulsossimetro si sta scaricando (es. suppongo sia scarico a 2.5V)
            return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro quasi scarico"
            #return [5, ID_P]

        if max(PI)<4: # Cercando su internet, la soglia per una lettura attendibile è al 4%
            # Se nessuna lettura attendibile, inutile proseguire
            return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            #return [6, ID_P]

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
            return f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
        
        pulse=np.std(pulse)

        if pulse>5:
            return f"ATTENZIONE, il paziente {ID_P} è in un possibile stato di fibrillazione"