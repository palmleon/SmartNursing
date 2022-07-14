import time
from MyMQTT import *
import json
import requests 


class light_patient_room_monitor() :
    def __init__(self) :
        self.conf_file = json.load(open('config.json'))
        self.serviceId = int(self.conf_file['serviceId'])
        self.serviceName = self.conf_file['serviceName']
        r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
            'serviceID' : self.serviceId,
            'name' : self.serviceName
        }))
        while r.ok != True :
            r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
            'serviceID' : self.serviceId,
            'name' : self.serviceName
        }))
        r = requests.get(self.conf_file['host']+"/city")
        c = r.json()
        r = requests.get(self.conf_file['host']+"/api-weather")
        a = r.json()
        self.urlApi = a+c
        r = requests.get(self.conf_file['host']+"/message-broker")
        mb = r.json()
        self.mqttClient = MyMQTT(self.serviceName,mb['name'],mb['port'],self)
        r = requests.get(self.conf_file['host']+"/patient-room-light-base-topic")
        t = r.json()
        self.subscribeTopic = t+"+"
        r = requests.get(self.conf_file['host']+"/patient-room-light-command-base-topic")
        c = r.json()
        self.commandTopic = c
        self.__baseMessage={"bn" : self.serviceName,"bt" : 0,"e" : {"n":"luminosity","u":"/","v":0}}
        self.mqttClient.start()
        time.sleep(2)
        self.mqttClient.mySubscribe(self.subscribeTopic)
        self.cloudCoverTheresold = self.conf_file['cloud-cover-theresold']
        self.visibilityTheresold = self.conf_file['visibility-theresold']

    def updateService(self) :
        while True :
            time.sleep(100)
            r = requests.put(self.conf_file['host']+"/update-service",data = json.dumps({
                'serviceID' : self.serviceId,
                'name' :self.serviceName
            }))
    
    def setLuminosity(self) :
        r = requests.get(self.urlApi)
        files = dict(r.json())
        if files['current']['is_day'] == 'no' :
            return 100
        elif files['current']['cloudcover'] > self.cloudCoverTheresold : #cloud cover è la percentuale di nuvolosità
            return 75
        elif  files['current']['visibility'] < self.visibilityTheresold : #visibility è la visibilita in km 
            return 60
        else : 
            return 15
    
    def notify(self,topic,payload) :
        message = dict(json.loads(payload))
        room = topic.split("/")[-1]
        print('ricevo dato',message['e']['v'])
        if message['e']['v'] == 1 : 
            luminosity = self.setLuminosity()  
            self.__baseMessage['bt'] = time.time()
            publishTopic = self.commandTopic+room
            self.__baseMessage['e']['v'] = luminosity
            self.mqttClient.myPublish(publishTopic,self.__baseMessage)     
            print("command "+str(self.__baseMessage))#rimuovere
    
        

        

if __name__ == "__main__" :
    light_patient_room_monitor_istnace = light_patient_room_monitor()
    light_patient_room_monitor_istnace.updateService()
    #while True :
    #    pass
