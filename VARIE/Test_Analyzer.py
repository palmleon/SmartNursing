from Fibrillation_Analyzer import *
from Patient_monitor_Analyzer import *
from random import randint

if __name__=="__main__":
    F=Fibrillation_Monitor()
    P=Patient_Monitor()

    x=""
    while x!="stop":
        b=randint(2,3)
        t=randint(30,40)
        print(f"\nTemperature: {t}")
        print(f"Battery: {b}")
        print(P.Temperature("Antonio",t,b))

        Pi=[randint(4,100) for i in range(9)]
        print(f"Stringa PI generata: {Pi}")
        s=[randint(94,100) for i in range(9)]
        print(f"Stringa sat generata: {s}")
        p=[randint(65,145) for i in range(9)]
        print(f"Stringa pulse generata: {p}")

        #print(P.Pulse("Antonio", Pi,p,s,b)) # Se si vuole testare la fibrillazione, si deve commentare questo metodo, altrimenti modifica anche p facendo il pop al suo interno
        print(F.fibrillation("Antonio",Pi,p,b))

        x=input()