from MyMQTT import MyMQTT
import time
from random import randint
import json

class Publisher_Test():
    def __init__(self):
        self.client = MyMQTT("aksjfgaj","test.mosquitto.org", 1883, self)
        self.client.start()
        time.sleep(5)
        # Subscribing
        self.client.mySubscribe("group01/IoTproject/PatientAlarm/Antonio")
    
    def send(self):
        b=randint(3,3)
        t=randint(37,37)
        print(f"\nTemperature: {t}")
        print(f"Battery: {b}")

        Pi=[randint(4,20) for i in range(9)]
        print(f"Stringa PI generata: {Pi}")
        s=[randint(96,96) for i in range(9)]
        print(f"Stringa sat generata: {s}")
        p=[randint(141,141) for i in range(9)]
        print(f"Stringa pulse generata: {p}")

        msg_sat={"bn" : "ID_sat", "bt" : time.time(), "e" : [{ "n":"battery", "u" : "V", "v" :b }, { "n":"perfusion index", "u" : "", "v" :Pi }, {"n":"saturation", "u" : "perc" , "v":s}, {"n":"pulse rate" , "u" : "bpm" , "v" : p}]}
        msg_temp={"bn" : "ID_temp", "bt" : time.time(), "e" : [{ "n":"battery", "u" : "V", "v" :b }, { "n":"temperature", "u" : "cel", "v" :t }]}

        self.client.myPublish("group01/IoTProject/Patient/Pulsation/Antonio",msg_sat)
        time.sleep(10)
        self.client.myPublish("group01/IoTProject/Patient/Temperature/Antonio",msg_temp)
        print("All published\n")


    def notify(self,topic,msg): # Metodo che analizza i dati arrivati e li stampa
        msg=json.loads(msg)
        ID_P=topic.split("/")[-1]
        print(f"Arrivato Paziente {ID_P}")
        print(msg)

if __name__=="__main__":
  P=Publisher_Test()
  while True:
    time.sleep(10)
    P.send()

