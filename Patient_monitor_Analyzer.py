import numpy as np

class Patient_Monitor():
    '''
    Suppongo che la classe di elaborazione generi solo i messaggi da mandare a telegram (tramite classe client).
    I dati da mandare a Thingspeak, dato che non devono essere elaborati prima, li manderà direttamente
    il message broker a Thingspeak in modo da potersi sottoscrivere a specifico ID_paziente e quindi
    specifico ID_pulse e ID_Termo, per quanto riguarda sia dati registrati che batteria'''   


    '''
    ATTENZIONE si dovrebbe pensare ad un modo (eventualmente nel client) per cui,
    dopo aver restituito un messaggio di emergenza, si silenzi per un po' di tempo. Altrimenti, se si riceve
    per lo stesso paziente una segnalazione di warning ogni 10s, l'infermiere impazzisce
    (considerando più pazienti presenti).

    Si può anche pensare che l'infermiere, una volta ricevuto il messaggio non riceve più altri warning per quel paziente
    e che ritorna a riceverli se si verifica una di due condizioni: preme un tasto di conferma su telegram
    (scrivendo tipo /ok [paziente ID] e si genera quindi una richiesta GET verso il servizio client
    (nell'url metti l'ID PZ) che riattiva l'analisi) o passa più di tot tempo''' # Deve farlo Telegram


    '''
    I Return sono scritti in due modi possibili:
    -return dell'intera stringa del messaggio da far vedere all'infermiere
    -return con codice allarme (che corrisponde ad un messaggio specifico) e valori da stampare (se serve, anche ID)
    Nel secondo caso il bot telegram, una volta ricevuto il messaggio, associa ad un codice allarme
    un template di stringa da riempire con i campi necessari.
    In questo modo, si risparmia sui bit da inviare sulla rete (minor latenza, minor probabilità di errore)''' # Da verificare successivamente


    def __init__(self,ID_P,ID_pulse,ID_Termo):
        self.__ID_P=ID_P
        self.__ID_Pulse=ID_pulse
        self.__ID_Termo=ID_Termo

    def Temperature(self,incoming,battery):
        # Suppongo arrivi un valore ogni 1m (1 solo valore, niente lista, quindi niente media)

        # battery è la sola tensione di batteria
        if battery<2.8: # Per informare che il termometro si sta scaricando (es. suppongo sia scarico a 2.5V)
            return f"ATTENZIONE, il paziente {self.__ID_P} ha il termometro quasi scarico"
            #return [1, self.__ID_P]

        # incoming è solo il valore di temperatura
        if incoming<=35:# Il sensore è mal posizionato
            #return f"ATTENZIONE, il paziente {self.__ID_P} ha il termometro mal posizionato"
            return [2, self.__ID_P]
        if incoming<36:
            #return f"ATTENZIONE, il paziente {self.__ID_P} ha una temperatura bassa, pari a {incoming}"
            return [3, self.__ID_P, incoming]
        if incoming>=37:
            #return f"ATTENZIONE, il paziente {self.__ID_P} ha febbre, con temperatura pari a {incoming}"
            return [4, self.__ID_P, incoming]
    
    def Pulse(self,PI,pulse,sat,battery):
        # Suppongo, per ogni input, arrivi una stringa ogni  10s, con fc=1Hz.
        # Battery, potrebbe essere anche un solo valore ogni 10s(discorso di ridurre i bit mandati)
        
        # battery è la sola tensione di batteria
        if battery<2.8:# Per informare che il pulsossimetro si sta scaricando (es. suppongo sia scarico a 2.5V)
            #return f"ATTENZIONE, il paziente {self.__ID_P} ha il pulsossimetro quasi scarico"
            return [5, self.__ID_P]

        if max(PI)<4: # Cercando su internet, la soglia per una lettura attendibile è al 4%
            # Se nessuna lettura attendibile, inutile proseguire
            #return f"ATTENZIONE, il paziente {self.__ID_P} ha il pulsossimetro mal posizionato o l'ha rimosso"
            return [6, self.__ID_P]

        to_remove=[]
        for i in range(PI):
            if PI[i]<4:
                # Rimuovo dalla stringa eventuali valori non attendibili
                to_remove.append(i)
        to_remove.sort(reverse=True)
        for rm in to_remove:
            pulse.pop(rm)
            sat.pop(rm)
        
        pulse=np.mean(pulse)
        sat=np.mean(sat)

        #r=""
        r=[]
        if sat<=95:
            r=f"ATTENZIONE, il paziente {self.__ID_P} è in ipossia. Saturazione al {sat} %\n"
            #r=[[7, self.__ID_P, sat]]
        if pulse<70:
            #r+= f"ATTENZIONE, il paziente {self.__ID_P} ha un battito cardiaco basso: {pulse} bpm"
            r+=[[8, self.__ID_P, pulse]]
        elif pulse>140:
            #r+=f"ATTENZIONE, il paziente {self.__ID_P} ha un battito cardiaco alto: {pulse} bpm"
            r+=[[9, self.__ID_P, pulse]]
            
        if len(r)>2:
            return r