from Patient_monitor_Analyzer import *
from MyMQTT import MyMQTT
import time
import json
import requests

class Patient_Monitor_client():
  def __init__(self):
    # Apertura file di configurazione
    print("Lettura file config\n")
    fp=open('Patient_monitor_config.json')
    conf_file = json.load(fp)
    fp.close
    #Acquisizione ID,nome e url registro
    self.__clientID=conf_file["serviceID"]
    self.__name=conf_file["name"]
    self.__register=conf_file["host"]
    # Acquisizione template alert e i vari alert
    self.__alert=conf_file["template_alarm"]
    messagesdict=conf_file["alarm_messages"]
    # Iscrizione al registro
    print("iscrizione al registro\n")
    r = requests.post(self.__register+"/add-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
    #print(r)
    
    # Richiesta dati broker al registro
    print("Richiesta dati al registro\n")
    r = requests.get(self.__register+"/message-broker")
    mb = r.json()
    self.__broker=mb['name']
    self.__port=mb['port']
    # Richiesta dei topic di subscribe e publish
    r = requests.get(self.__register+"/patient-saturation-base-topic")
    mb = r.json()
    # Per ora, in mb abbiamo direttamente il topic, non coppia key/value
    self.__topic_sub_P=mb+"+"

    r = requests.get(self.__register+"/patient-temperature-base-topic")
    mb = r.json()
    # Per ora, in mb abbiamo direttamente il topic, non coppia key/value
    self.__topic_sub_T=mb+"+"

    r = requests.get(self.__register+"/alarm-base-topic")
    mb = r.json()
    # Per ora, in mb abbiamo direttamente il topic, non coppia key/value
    self.__base_topic_pub=mb
    
    # Creating analyzer
    self.analyzer=Patient_Monitor(messagesdict)

    # Creating client
    print("Istanziamento Client\n")
    self.client = MyMQTT(self.__name, self.__broker, self.__port, self)

    # Starting client
    self.client.start()
    time.sleep(2)

    # Subscribing
    #print(f"Sottoscrizione al topic: {self.__topic_sub_T}\n")
    self.client.mySubscribe(self.__topic_sub_T)

    #print(f"Sottoscrizione al topic: {self.__topic_sub_P}\n")
    self.client.mySubscribe(self.__topic_sub_P)
  
  def updateService(self) :
    while True :
      time.sleep(40)
      r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
      #print(r)


  def notify(self,topic,msg): # Metodo che analizza i dati arrivati utilizzando i metodi dell'analyzer e, in caso, pubblica i warning
    print(f"messaggio arrivato da topic: {topic}\n")
    msg=json.loads(msg)
    ID_P=topic.split("/")[-1] # Prendo l'ID del PZ alla fine del topic

    
    evento=msg["e"] # Prendo la lista degli eventi
    
    # Inizializzazioni
    # battery non necessario, altrimenti vuol dire che c'è stato errore
    # Pi dovrebbe essere lungo quanto gli altri vettori, basta inizializzare solo questo
    Pi=[]
    temp=-1
    for ev in evento:
      if ev["n"]=="battery":
        battery=ev["v"]

      if ev["n"]=="perfusion index":
        Pi=ev["v"]
      
      if ev["n"]=="saturation":
        sat=ev["v"]
      
      if ev["n"]=="pulse rate":
        pulse=ev["v"]
      
      if ev["n"]=="temperature":
        temp=ev["v"]
    
    if temp>-1:
      print(f"Ottenuti: batteria={battery} e temperatura:{temp}\n")
      r=self.analyzer.Temperature(ID_P,temp,battery)
      print(f"Risposta ottenuta:{r}\n")
      if r!=None:
        to_pub=self.__alert
        #to_pub["ID_PZ"]=ID_P
        to_pub["alert"]=r
        to_pub["time"]=time.localtime()
        # Publish alert
        print("Invio allarme per temperature\n")
        self.client.myPublish(self.__base_topic_pub+ID_P,to_pub)
    
    if len(Pi)>1:
      print(f"Ottenuti: batteria={battery} e liste dei parametri\n")
      r=self.analyzer.Pulse(ID_P,Pi,pulse,sat,battery)
      for alert in r:
        to_pub=self.__alert
        #to_pub["ID_PZ"]=ID_P
        to_pub["alert"]=alert
        to_pub["time"]=time.localtime()
        # Publish alert
        print("Invio allarme per oximeter\n")
        self.client.myPublish(self.__base_topic_pub+ID_P,to_pub)

if __name__=="__main__":
  F=Patient_Monitor_client()
  F.updateService()
  #while True:
    #pass