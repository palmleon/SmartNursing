import numpy as np

class Patient_Monitor():
    def __init__(self):
        pass

    def Temperature(self,ID_P,incoming,battery):
        # Suppongo arrivi un valore ogni 1m (1 solo valore, niente lista, quindi niente media)

        # battery è la sola tensione di batteria
        if battery<2.8: # Per informare che il termometro si sta scaricando (es. suppongo sia scarico a 2.5V)
            r=f"ATTENZIONE, il paziente {ID_P} ha il termometro quasi scarico"
            return r
            #return [1, self.__ID_P]

        # incoming è solo il valore di temperatura
        if incoming<=35:# Il sensore è mal posizionato
            r=f"ATTENZIONE, il paziente {ID_P} ha il termometro mal posizionato"
            return r
            #return [2, ID_P]
        if incoming<36:
            r=f"ATTENZIONE, il paziente {ID_P} ha una temperatura bassa, pari a {incoming}"
            return r
            #return [3, ID_P, incoming]
        if incoming>=37:
            r=f"ATTENZIONE, il paziente {ID_P} ha febbre, con temperatura pari a {incoming}"
            return r
            #return [4, ID_P, incoming]
    
    def Pulse(self,ID_P,PI,pulse,sat,battery):
        # Suppongo, per ogni input, arrivi una stringa ogni  10s, con fc=1Hz.
        # Battery, potrebbe essere anche un solo valore ogni 10s(discorso di ridurre i bit mandati)
        
        # battery è la sola tensione di batteria
        if battery<2.8:# Per informare che il pulsossimetro si sta scaricando (es. suppongo sia scarico a 2.5V)
            r=f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro quasi scarico"
            return r
            #return [5, ID_P]

        if max(PI)<4: # Cercando su internet, la soglia per una lettura attendibile è al 4%
            # Se nessuna lettura attendibile, inutile proseguire
            r=f"ATTENZIONE, il paziente {ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            return r
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
            sat.pop(rm)
        print(f"Lista pulse ottenuta in patient: {pulse}")
        print(f"Lista sat ottenuta in patient: {sat}")
        
        pulse=np.mean(pulse)
        sat=np.mean(sat)

        r=""
        #r=[]
        if sat<=95:
            r=f"ATTENZIONE, il paziente {ID_P} è in ipossia. Saturazione al {sat} % \n"
            #r=[[7, self.__ID_P, sat]]
        if pulse<55:
            r+= f"ATTENZIONE, il paziente {ID_P} ha un battito cardiaco basso: {pulse} bpm"
            #r+=[[8, ID_P, pulse]]
        elif pulse>100:
            r+=f"ATTENZIONE, il paziente {ID_P} ha un battito cardiaco alto: {pulse} bpm"
            #r+=[[9, ID_P, pulse]]
            
        if len(r)>2:
            return r