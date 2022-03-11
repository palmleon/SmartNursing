from MyMQTT import MyMQTT
import time
from random import randint

class Publisher_Test():
    def __init__(self):
        self.client = MyMQTT("aksjfgaj","test.mosquitto.org", 1883, None)
        self.client.start()
    
    def send(self):
        b=randint(2,3)
        t=randint(30,40)
        print(f"\nTemperature: {t}")
        print(f"Battery: {b}")

        Pi=[randint(4,100) for i in range(9)]
        print(f"Stringa PI generata: {Pi}")
        s=[randint(94,100) for i in range(9)]
        #print(f"Stringa sat generata: {s}")
        p=[randint(65,145) for i in range(9)]
        print(f"Stringa pulse generata: {p}")

        msg_sat={"bn" : "ID_sat", "bt" : time.time(), "e" : [{ "n":"battery", "u" : "V", "v" :b }, { "n":"perfusion index", "u" : "", "v" :Pi }, {"n":"saturation", "u" : "perc" , "v":s}, {"n":"pulse rate" , "u" : "bpm" , "v" : p}]}
        msg_temp={"bn" : "ID_sat", "bt" : time.time(), "e" : [{ "n":"battery", "u" : "V", "v" :b }, { "n":"temperature", "u" : "cel", "v" :t }]}

        self.client.myPublish("group01/IoTProject/Patient/Pulsation/Antonio",msg_sat)
        time.sleep(20)
        self.client.myPublish("group01/IoTProject/Patient/Temperature/Antonio",msg_temp)

if __name__=="__main__":
  P=Publisher_Test()
  while True:
    time.sleep(10)
    P.send()

