from MyMQTT import MyMQTT
import time
import json

class Sub_Test():
    def __init__(self):
        self.client = MyMQTT("aksjfgaj","test.mosquitto.org", 1883, self)
        # Starting client
        self.client.start()
        time.sleep(2)
        # Subscribing
        self.client.mySubscribe("group01/IoTproject/PatientAlarm/Antonio")

    def notify(self,topic,msg): # Metodo che analizza i dati arrivati e li stampa
        msg=json.loads(msg)
        ID_P=topic.split("/")[-1]
        print(f"Arrivato Paziente {ID_P}")
        print(msg)

if __name__=="__main__":
  S=Sub_Test()
  while True:
    pass