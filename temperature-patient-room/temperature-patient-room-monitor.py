import time
from MyMQTT import *
import json
import requests 
import datetime

class temperature_patient_room_monitor() :
    def __init__(self) :
        self.__fp = open('config.json')
        self.__conf_file = json.load(self.__fp)
        self.__serviceId = int(self.__conf_file['serviceId'])
        self.__serviceName = self.__conf_file['serviceName']
        self.__updateTimeInSecond = int(self.__conf_file['updateTimeInSecond'])
        try : 
            r = requests.post(self.__conf_file['host']+"/add-service",data = json.dumps({
                'serviceID' : self.__serviceId,
                'name' : self.__serviceName
            }))
            r = requests.get(self.__conf_file['host']+"/message-broker")
            mb = r.json()
            self.__mqttClient = MyMQTT('temperature-patient-room-monitor',mb['name'],mb['port'],self)
            r = requests.get(self.__conf_file['host']+"/patient-room-temperature-base-topic")
            t = r.json()
            self.__subscribeTopic = t+"+"
            
            r = requests.get(self.__conf_file['host']+"/patient-room-hourly-scheduling")
            t = r.json()
            self.__hourlyScheduling = t
            r = requests.get(self.__conf_file['host']+"/patient-room-temperature-command-base-topic")
            c = r.json()
            self.__commandTopic = c
            self.__baseMessage=self.__conf_file['base-message']
            self.__fp.close()
        except :
            print("ERROR: init failed, restart the container")

        self.__mqttClient.start()
        self.__mqttClient.mySubscribe(self.__subscribeTopic)
        #print('start')

    def updateService(self) :
        while True :
            time.sleep(self.__updateTimeInSecond)
            requestOK = False
            while requestOK != True :
                try :
                    r = requests.put(self.__conf_file['host']+"/update-service",data = json.dumps({
                        'serviceID' : self.__serviceId,
                        'name' : self.__serviceName
                    }))
                except :
                    print("ERROR: update service failed, retrying")
    

    def getSeason(self) :
        doy = datetime.datetime.today().timetuple().tm_yday
        # "day of year" ranges for the northern hemisphere
        spring = range(80, 172)
        summer = range(172, 264)
        fall = range(264, 355)
        # winter = everything else

        if doy in spring:
            season = 'hot'
        elif doy in summer:
            season = 'hot'
        elif doy in fall:
            season = 'cold'
        else:
            season = 'cold'
        return season

    def defineCommand(self,desiredTemperature,currentTemperature,season) :
        command = 0
        if season == 'hot' and  currentTemperature > desiredTemperature :
                command = 1
        if season == 'cold' and currentTemperature < desiredTemperature : 
                command = 1
        return command

    def expectedPresence(self,currentHour) :
        for rangeHour in self.__hourlyScheduling['expected-range-hours'] :
            if currentHour >= rangeHour[0] and currentHour <= rangeHour[1] :
                return True
        return False


    def setTemperature(self,room,presence,currentTemperature) :
        currentHour =  datetime.datetime.now().hour
        print('current hour: ',currentHour,'\n')
        season = self.getSeason()
        try :
            r = requests.get(self.__conf_file['host']+"/room-temperature/"+room)
            t = r.json()
            desiredTemperature = t['desired-temperature']
        except :
            print("ERROR: unable to get the desired temperature")
            return
        if  currentHour >= self.__hourlyScheduling['night'][0] or currentHour <= self.__hourlyScheduling['night'][1] : #night
            return self.defineCommand(desiredTemperature,currentTemperature,season)
        else : #not night
            if presence == True :
                return self.defineCommand(desiredTemperature,currentTemperature,season)
            else : #not night and not presence 
                expected = self.expectedPresence(currentHour)
                if expected == True and season == 'hot':
                    return self.defineCommand(desiredTemperature+2,currentTemperature,season)
                elif expected == True and season == 'cold':
                    return self.defineCommand(desiredTemperature-2,currentTemperature,season)
                elif expected == False and season == 'hot':
                    return self.defineCommand(desiredTemperature+4,currentTemperature,season)
                elif expected == False and season == 'cold':
                    return self.defineCommand(desiredTemperature-4,currentTemperature,season)
            
    
    def notify(self,topic,payload) :
        message = dict(json.loads(payload))
        #suppongo di ricevere nel messaggio id room sotto la chiave room ed sotto la chiave presence  l info se utente c'è o meno e sotto la chiave temperature la temperatue corrente
        room = topic.split("/")[-1]
        
        command = self.setTemperature(room,message['e'][0]['v'],message['e'][1]['v'])  
        self.__baseMessage['bt'] = time.time()
        topicPublish = self.__commandTopic+room
        self.__baseMessage['e']['v'] = command
        self.__mqttClient.myPublish(topicPublish,self.__baseMessage)     
        print("command sends:\n"+str(self.__baseMessage))
    
        

        

if __name__ == "__main__" :
    temperature_patient_room_monitor_istnace = temperature_patient_room_monitor()
    temperature_patient_room_monitor_istnace.updateService()
    #while True :
    #    pass
