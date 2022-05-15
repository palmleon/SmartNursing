from Fibrillation_Analyzer import *
from MyMQTT import MyMQTT
import time
import json
import requests

class Fibrillation_Monitor_client():
  def __init__(self):
    # Apertura file di configurazione
    fp=open('Fibrillation_config.json')
    conf_file = json.load(fp)
    fp.close
    #Acquisizione ID, nome e url registro
    self.__clientID=conf_file["serviceID"]
    self.__name=conf_file["name"]
    self.__register=conf_file["host"]
    # Generazione template alert
    self.__alert=conf_file["template_allarm"]
    # Iscrizione al registro
    r = requests.post(self.__register+"/add-service",data= json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))

    # Richiesta dati broker al registro
    r = requests.get(self.__register+"/message-broker")
    mb = r.json()
    self.__broker=mb['name']
    self.__port=mb['port']
    # Richiesta dei topic di subscribe e publish
    r = requests.get(self.__register+"/patient-saturation-base-topic")
    mb = r.json()
    # In mb abbiamo il topic
    self.__topic_sub=mb+"+"

    r = requests.get(self.__register+"/alarm-base-topic")
    mb = r.json()
    # In mb abbiamo il topic
    self.__base_topic_pub=mb

    # Creating analyzer
    self.analyzer=Fibrillation_Monitor()

    # Creating client
    self.client = MyMQTT(self.__name, self.__broker, self.__port, self)

    # Starting client
    self.client.start()
    time.sleep(2)

    # Subscribing
    self.client.mySubscribe(self.__topic_sub)
  
  def updateService(self) :
    while True :
      time.sleep(100)
      r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))

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
        to_pub=self.__alert
        #to_pub["ID_PZ"]=ID_P
        to_pub["alert"]=r
        to_pub["time"]=time.localtime()
        # Publish alert
        self.client.myPublish(self.__base_topic_pub+ID_P,to_pub)
        print("DEBUG : pubblico allarme per fibrillation ")
        #print(f"Published: {to_pub}\nat topic: {self.__base_topic_pub}{ID_P}")

if __name__=="__main__":
  F=Fibrillation_Monitor_client()
  F.updateService()
  #while True:
    #pass