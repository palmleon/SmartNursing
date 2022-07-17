import time
from MyMQTT import *
import json
import requests 


class light_patient_room_monitor() :
    def __init__(self) :
        self.__fp = open('config.json')
        self.__conf_file = json.load(self.__fp)
        self.__serviceID = int(self.__conf_file['serviceId'])
        self.__serviceName = self.__conf_file['serviceName']
        self.__updateTimeInMinutes = int(self.__conf_file['update-time-in-minutes'])
        try :
            r = requests.post(self.__conf_file['host']+"/add-service",data =json.dumps( {
                'serviceID' : self.__serviceID,
                'name' : self.__serviceName
            }))
            r = requests.get(self.__conf_file['host']+"/city")
            c = r.json()
            r = requests.get(self.__conf_file['host']+"/api-weather")
            a = r.json()
            self.__urlApi = a+c
            r = requests.get(self.__conf_file['host']+"/message-broker")
            mb = r.json()
            self.__mqttClient = MyMQTT(self.__serviceName,mb['name'],mb['port'],self)
            r = requests.get(self.__conf_file['host']+"/patient-room-light-base-topic")
            t = r.json()
            self.__subscribeTopic = t+"+"
            r = requests.get(self.__conf_file['host']+"/patient-room-light-command-base-topic")
            c = r.json()
            self.__commandTopic = c
            self.__baseMessage=self.__conf_file['base-message']
            self.__mqttClient.start()
            time.sleep(2)
            self.__mqttClient.mySubscribe(self.__subscribeTopic)
            self.cloudCoverTheresold = self.__conf_file['cloud-cover-theresold']
            self.visibilityTheresold = self.__conf_file['visibility-theresold']
            self.__fp.close()
        except :
            print("ERROR: init failed, restart the container")
            exit(-1)

    def updateService(self) :
        while True :
            time.sleep(self.__updateTimeInMinutes*60)
           
            try : 
                r = requests.put(self.__conf_file['host']+"/update-service",data = json.dumps({
                        'serviceID' : self.__serviceID,
                        'name' :self.__serviceName
                    }))
                if r.ok == False :
                    print("ERROR: update service failed")
            except :
                print("ERROR: update service failed")
    
    def setLuminosity(self) :
        try :
            r = requests.get(self.__urlApi)
            files = dict(r.json())
        except :
            print("ERROR: unable to get the current wheater conditions")
            return
        if files['current']['is_day'] == 'no' :
            return 100
        elif files['current']['cloudcover'] > self.cloudCoverTheresold : #cloud cover 
            return 75
        elif  files['current']['visibility'] < self.visibilityTheresold : #visibility  
            return 60
        else : 
            return 15
    
    def notify(self,topic,payload) :
        message = dict(json.loads(payload))
        room = topic.split("/")[-1]
        if message['e']['v'] == 1 : 
            luminosity = self.setLuminosity()  
            self.__baseMessage['bt'] = time.time()
            publishTopic = self.__commandTopic+room
            self.__baseMessage['e']['v'] = luminosity
            self.__mqttClient.myPublish(publishTopic,self.__baseMessage)     
            print("command sends:\n"+str(self.__baseMessage))
    
        

        

if __name__ == "__main__" :
    light_patient_room_monitor_istnace = light_patient_room_monitor()
    light_patient_room_monitor_istnace.updateService()
    #while True :
    #    pass
