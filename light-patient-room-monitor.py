from MyMQTT import *
import json
import requests 


class light_patient_room_monitor() :
    def __init__(self) :
        #FARE POST DEL SERVIZIO PER INSERIRLO
        r = requests.get("https://localhost:8080/catalog/city")
        c = r.json()
        self.urlApi = "http://api.weatherstack.com/current?access_key=36fcb02003026b9fae56e4c0a5a228fe&query="+c['city']
        r = requests.get("https://localhost:8080/catalog/message-broker")
        mb = r.json()
        self.mqttClient = MyMQTT('light-patient-room-monitor',mb['name'],mb['port'],self)
        r = requests.get("https://localhost:8080/catalog/patient-room-base-topic")
        t = r.json()
        self.subscribeTopic = t['patient-room-base-topic']+"+/"
        r = requests.get("https://localhost:8080/catalog/patient-room-command-base-topic")
        c = r.json()
        self.commandTopic = c['patient-room-command-base-topic']
        self.mqttClient.start()
        self.mqttClient.mySubscribe(self.subscribeTopic)
    
    def setLuminosity(self) :
        r = requests.get(self.urlApi)
        files = dict(r.json())
        if files['current']['is_day'] == 'no' :
            return 100
        else :
            return 80
    
    def notify(self,topic,payload) :
        message = dict(json.loads(payload))
        room = message['room']
        if message['open'] == 1 :
            #fai la richiesta 
            # invoca funzione che ritorna  
            luminosity = self.setLuminosity()  
            MyMQTT.myPublish(self.commandTopic,{'l' : luminosity })     

    
        

        

if __name__ == "__main__" :
    light_patient_room_monitor_istnace = light_patient_room_monitor()
    #invocare thread che esegue la registrazione del servizio
    while True :
        pass
