import time
class TMonitor():
    def __init__(self,T):
        #T=temperatura impostata dall'infermiere
        self.__T=T
        self.__nigth=[22*60,8*60]
        self.__inroom=[9*60,12*60,14*60,19*60]
        self.__summer=[4,9]
    def monitor(self,presence,ok): #ok=c'è un paziente registrato nella stanza
        t=time.localtime()
        s=t[3]*60+t[4]
        if ok==1: # La stanza è associata ad un pz
            if (s>self.__nigth[0] and s<12*60) or (s>0 and s<8*60): # E' notte
                return self.__T
            else: # Non è notte
                if presence==1: # E' in stanza
                    return self.__T
                else: # Non è in stanza
                    if (s>self.__inroom[0] and s<self.__inroom[1]) or (s>self.__inroom[2] and s<self.__inroom[3]): # E' previsto in stanza
                        if t[1]>self.__summer[0] and t[1]<self.__summer[1]: # E' in estate
                            return self.__T+2
                        else: # E' inverno
                            return self.__T-2
                    else: # Non è previsto in stanza
                        if t[1]>self.__summer[0] and t[1]<self.__summer[1]: # E' in estate
                            return self.__T+4
                        else: # E' inverno
                            return self.__T-4
        else: # La stanza non è associata ad un pz
            if t[1]>self.__summer[0] and t[1]<self.__summer[1]: # E' in estate
                return self.__T+4
            else: # E' inverno
                return self.__T-4

if __name__=="__main__":
    T=int(input("Insert T:"))
    TM=TMonitor(T)
    while True:
        ok=int(input("Insert ok: "))
        if ok==1:
            presence=int(input("Paziente è nella stanza(1) o no(0): "))
        else:
            presence=None
        print(TM.monitor(presence,ok))
