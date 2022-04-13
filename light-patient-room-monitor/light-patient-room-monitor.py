from pydoc import doc
import time
from MyMQTT import *
import json
import requests 


class light_patient_room_monitor() :
    def __init__(self) :

        self.conf_file = json.load(open('config.json'))
        r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
            'serviceID' : 1,
            'name' : 'light-patient-room-monitor'
        }))
        if r.ok == False :
            print('Error adding the service')
        r = requests.get(self.conf_file['host']+"/city")
        c = r.json()
        r = requests.get(self.conf_file['host']+"/api-weather")
        a = r.json()
        self.urlApi = a+c
        r = requests.get(self.conf_file['host']+"/message-broker")
        mb = r.json()
        self.mqttClient = MyMQTT('light-patient-room-monitor-service1',mb['name'],mb['port'],self)
        r = requests.get(self.conf_file['host']+"/patient-room-base-topic")
        t = r.json()
        self.subscribeTopic = t+"+"
        r = requests.get(self.conf_file['host']+"/patient-room-command-base-topic")
        c = r.json()
        self.commandTopic = c
        self.__baseMessage={"bn" : "light-patient-room-monitor","bt":0,"r":0,"c" : {"n":"luminosity","u":"/","v":0}}
        self.mqttClient.start()
        self.mqttClient.mySubscribe(self.subscribeTopic)

    def updateService(self) :
        while True :
            time.sleep(100)
            r = requests.put(self.conf_file['host']+"/update-service",data = json.dumps({
                'serviceID' : 1,
                'name' : 'light-patient-room-monitor'
            }))
    
    def setLuminosity(self) :
        #migliorare questo calcolo
        r = requests.get(self.urlApi)
        files = dict(r.json())
        if files['current']['is_day'] == 'no' :
            return 100
        elif files['current']['cloudcover'] > 60 : #cloud cover è la percentuale di nuvolosità
            return 75
        elif  files['current']['visibility'] < 5 : #visibility è la visibilita in km 
            return 60
        else : 
            return 15
    
    def notify(self,topic,payload) :
        message = dict(json.loads(payload))
        #prendere room id dal topic
        room = topic.split("/")[-1]
        if message['e'][0]['v'] == 1 :
            #fai la richiesta 
            # invoca funzione che ritorna  
            luminosity = self.setLuminosity()  
            self.__baseMessage['bt'] = time.time()
            self.__baseMessage['r'] = room
            self.__baseMessage['c']['v'] = luminosity
            self.mqttClient.myPublish(self.commandTopic,self.__baseMessage)     
            print("command "+str({'switch' : luminosity, 'room' : room }))#rimuovere
    
        

        

if __name__ == "__main__" :
    light_patient_room_monitor_istnace = light_patient_room_monitor()
    #invocare thread che esegue la registrazione del servizio, che forse è opzionale
    light_patient_room_monitor_istnace.updateService()
    #while True :
    #    pass
