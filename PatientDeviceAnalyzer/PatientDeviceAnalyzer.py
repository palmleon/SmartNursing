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
    self.__allert=conf_file["template_allarm"]
    # Iscrizione al registro
    r = requests.post(self.__register+"/add-service",data= json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
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
          # Invio del messaggio di errore a telegram MQTT
          print(f"Dispositivo {device} mancante")
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
