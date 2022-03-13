from Fibrillation_Analyzer import *
from MyMQTT import MyMQTT
import time
import json

class Fibrillation_Monitor_client():
  def __init__(self):
    # Qui andrà la richiesta al registro per prendere tutti i dati necessari
    self.__clientID="clientID"
    self.__broker="test.mosquitto.org"
    self.__port=1883
    self.__topic_sub="group01/IoTProject/Patient/Pulsation/+"
    self.__base_topic_pub="group01/IoTproject/PatientAlarm/"
    # Generazione template allert
    self.__allert={"ID_PZ":"","allert":"","time":0}

    # Creating analyzer
    self.analyzer=Fibrillation_Monitor()

    # Creating client
    self.client = MyMQTT(self.__clientID, self.__broker, self.__port, self)

    # Starting client
    self.client.start()
    time.sleep(2)

    # Subscribing
    self.client.mySubscribe(self.__topic_sub)

  def notify(self,topic,msg): # Metodo che analizza i dati arrivati utilizzando i metodi dell'analyzer e, in caso, pubblica i warning
    msg=json.loads(msg)
    ID_P=topic.split("/")[-1] # Prendo l'ID del PZ alla fine del topic

    evento=msg["e"] # Prendo la lista degli eventi
    
    # Inizializzazioni
    # battery non necessario, altrimenti vuol dire che c'è stato errore
    # Pi dovrebbe essere lungo quanto gli altri vettori, basta inizializzare solo questo
    Pi=[]
    for ev in evento:
      if ev["n"]=="battery":
        battery=ev["v"]

      if ev["n"]=="perfusion index":
        Pi=ev["v"]
      
      if ev["n"]=="saturation":
        sat=ev["v"]
      
      if ev["n"]=="pulse rate":
        pulse=ev["v"]
    
    if len(Pi)>1:
      r=self.analyzer.fibrillation(ID_P,Pi,pulse,battery)
      if r!=None:
        to_pub=self.__allert
        to_pub["ID_PZ"]=ID_P
        to_pub["allert"]=r
        to_pub["time"]=time.time()
        # Publish allert
        self.client.myPublish(self.__base_topic_pub+ID_P,to_pub)
        #print(f"Published: {to_pub}\nat topic: {self.__base_topic_pub}{ID_P}")

if __name__=="__main__":
  F=Fibrillation_Monitor_client()
  while True:
    pass