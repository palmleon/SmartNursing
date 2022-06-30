from MyMQTT import MyMQTT
import time
import json
import requests
import threading

class PatientDeviceAnalyzer():
  def __init__(self):
    # Apertura file di configurazione
    fp=open('PatientDeviceAnalyzer_config.json')
    conf_file = json.load(fp)
    fp.close
    # Acquisizione ID, nome e url registro
    self.__clientID=conf_file["serviceID"]
    self.__name=conf_file["name"]
    self.__register=conf_file["host"]
    # Generazione template alert
    self.__alert=conf_file["template_alarm"]
    # Iscrizione al registro
    r=requests.post(self.__register+"/add-service",data= json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
    
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
    self.__hours=d["night"] # in teoria, carica una lista con d[0]=21 e d[1]=10
    #self.__flag=0 # Serve per sapere se è iniziata la notte (1) o meno(0)
    self.__devices=[] # Inizializzazione lista di dispositivi
  
  def control(self):
    while True:
      time.sleep(20)
      #Controllo su orario (è notte?)
      if time.localtime()[3]>=self.__hours[0] or time.localtime()[3]<=self.__hours[1]:
        # Richiesta dell'attuale lista dei pazienti (possibile uscita durante la notte)
        r = requests.get(self.__register+"/patients")
        patient_list=r.json()
        patient_IDs=[]
        for patient in patient_list:
          patient_IDs.append(patient["patientID"])
        # Richiesta dell'attuale lista dei device
        r = requests.get(self.__register+"/devices")
        all_devices=r.json()
        for patient in patient_IDs: #Si cerca l'ID del paziente nella lista dei device
          sensors=[]
          for device in all_devices:
            if "patientID" in device: #Verifica del tipo di sensore (se del paziente o della stanza)
              if patient==device["patientID"]:
                sensors.append(device["name"])
          if "patient temperature sensor" not in sensors:
            r=f"Il termometro del paziente {patient} è offline"
          elif "patient oximeter sensor" not in sensors:
            r=f"Il pulsossimetro del paziente {patient} è offline"
          print(r) #print di DEBUG
          if len(r)>1:
            #Creazione messaggio
            to_pub=self.__alert
            to_pub["alert"]=r
            to_pub["time"]=time.localtime()
            # Publicazione alert
            self.client.myPublish(self.__base_topic_pub+patient,to_pub)
  
  def updateService(self) :
    while True :
      time.sleep(100)
      r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))

if __name__ == "__main__" :
  A=PatientDeviceAnalyzer()
  t1 = threading.Thread(target=A.control)
  t2 = threading.Thread(target=A.updateService)
  t1.start()
  t2.start()
  t1.join()
  t2.join()
