from MyMQTT import MyMQTT
import time
import json
import requests
import cherrypy

class PatientDeviceAnalyzer():
  def __init__(self):
    # Apertura file di configurazione
    fp=open('DeviceAnalyzer_config.json')
    conf_file = json.load(fp)
    fp.close
    #Acquisizione ID, nome e url registro
    self.__clientID=conf_file["serviceID"]
    self.__name=conf_file["name"]
    self.__register=conf_file["host"]
    # Generazione template allert
    self.__alert=conf_file["template_alarm"]
    # Iscrizione al registro
    r = requests.post(self.__register+"/add-service",data= json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
    
    # Richiesta dati broker al registro
    r = requests.get(self.__register+"/message-broker")
    mb = r.json()
    self.__broker=mb['name']
    self.__port=mb['port']
    # Richiesta del topic di publish
    r = requests.get(self.__register+"/alarm-base-topic")
    self.__base_topic_pub = r.json()

    # Creating client
    self.client = MyMQTT(self.__name, self.__broker, self.__port, None)
    # Starting client
    self.client.start()
    time.sleep(2)

    # Richiesta table oraria
    r = requests.get(self.__register+"/patient-room-hourly-scheduling")
    d=r.json()
    self.__hours=d["night"] # in teoria, cambia in una lista con d[0]=21 e d[1]=10
    self.__flag=0 # Serve per sapere se è iniziata la notte (1) o meno(0)
    self.__devices=[] # Inizializzazione lista di dispositivi
  
  def control(self):
    #Controllo su orario (è notte?)
    if time.localtime()[3]>=self.__hours[0] or time.localtime()[3]<=self.__hours[1]:
      if self.__flag==0:
        # E' appena iniziata la notte
        self.__flag=1
        # Richiesta della lista dei device a inizio notte
        r = requests.get(self.__register+"/devices")
        devices=r.json()
        # devices è una lista di dizionari, estraggo solo gli ID
        for device in devices:
          self.__devices.append(device["deviceID"])

      # Richiesta dell'attuale lista dei device
      r = requests.get(self.__register+"/devices")
      actual_devices=r.json()
      actual=[]
      for device in actual_devices:
          actual.append(device["deviceID"])
      # Confronto
      for device in self.__devices:
        if device not in actual:
          ID_miss=device[:-1] #Prende l'Id del solo paziente
          if device[-1]=="o":
            sensor="saturimetro"
          else:
            sensor="termometro"
          r=f"Il {sensor} del paziente {ID_miss} è stato scollegato"
          # Invio del messaggio di errore a telegram MQTT
          print(r)
          #Creazione messaggio
          to_pub=self.__alert
          to_pub["alert"]=r
          to_pub["time"]=time.localtime()
          # Publicazione alert
          self.client.myPublish(self.__base_topic_pub+ID_miss,to_pub)
      # Aggiornamento lista dei dispositivi
      self.__devices=actual
    else: # E' giorno
      self.__flag=0
      self.__devices=[]
  
  def updateService(self) :
    while True :
      time.sleep(100)
      r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))

if __name__ == "__main__" :
  A=PatientDeviceAnalyzer()
