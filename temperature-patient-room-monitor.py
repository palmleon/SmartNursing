import time
from MyMQTT import *
import json
import requests 
import datetime

class temperature_patient_room_monitor() :
    def __init__(self) :
        
        self.conf_file = json.load(open('config.json'))

        r = requests.post(self.conf_file['host']+"/add-service",json.dumps(data = {
            'serviceID' : 3,
            'name' : 'temperature-patient-room-monitor'
        }))
        r = requests.get(self.conf_file['host']+"/message-broker")
        mb = r.json()
        self.mqttClient = MyMQTT('light-patient-room-monitor',mb['name'],mb['port'],self)
        r = requests.get(self.conf_file['host']+"/patient-room-base-topic")
        t = r.json()
        self.subscribeTopic = t+"+/"
        r = requests.get(self.conf_file['host']+"/desired-temperature")
        t = r.json()
        self.desiredTemperature = t
        r = requests.get(self.conf_file['host']+"/patient-room-hourly-scheduling")
        t = r.json()
        self.hourlyScheduling = t
        r = requests.get(self.conf_file['host']+"/patient-room-command-base-topic")
        c = r.json()
        self.commandTopic = c
        self.mqttClient.start()
        self.mqttClient.mySubscribe(self.subscribeTopic)

    def updateService(self) :
        while True :
            time.sleep(100)
            r = requests.put(self.conf_file['host']+"/update-service",json.dumps(data = {
                'serviceID' : 3,
                'name' : 'temperature-patient-room-monitor'
            }))
    

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
        command = 'off'
        if season == 'hot' and  currentTemperature > self.desiredTemperature :
                command = 'on'
        if season == 'cold' and currentTemperature < self.desiredTemperature : 
                command = 'on'
        return command

    def expectedPresence(self,currentHour) :
        for rangeHour in self.hourlyScheduling['expected-range-hours'] :
            if currentHour >= rangeHour[0] and currentHour <= rangeHour[1] :
                return True
        return False


    def setTemperature(self,presence,currentTemperature) :
        #migliorare questo calcolo
        currentHour =  datetime.datetime.now().hour
        season = self.getSeason()
        
        if  currentHour >= self.hourlyScheduling['night'][0] or currentHour <= self.hourlyScheduling['night'][1] : #night
            return self.defineCommand(self.desiredTemperature,currentTemperature,season)
        else : #not night
            if presence == True :
                return self.defineCommand(self.desiredTemperature,currentTemperature,season)
            else : #not night and not presence 
                expected = self.expectedPresence(currentHour)
                if expected == True and season == 'hot':
                    return self.defineCommand(self.desiredTemperature+2)
                elif expected == True and season == 'cold':
                    return self.defineCommand(self.desiredTemperature-2)
                elif expected == False and season == 'hot':
                    return self.defineCommand(self.desiredTemperature+4)
                elif expected == False and season == 'cold':
                    return self.defineCommand(self.desiredTemperature-4)
            
    
    def notify(self,topic,payload) :
        message = dict(json.loads(payload))
        #suppongo di ricevere nel messaggio id room sotto la chiave room ed sotto la chiave presence  l info se utente c'è o meno e sotto la chiave temperature la temperatue corrente
        room = message['room']
        if message['open'] == 1 :
            #fai la richiesta 
            # invoca funzione che ritorna  
            command = self.setTemperature(message['presence'],message['temperature'])  
            MyMQTT.myPublish(self.commandTopic,{'switch' : command, 'room' : room })     

    
        

        

if __name__ == "__main__" :
    temperature_patient_room_monitor_istnace = temperature_patient_room_monitor()
    #invocare thread che esegue la registrazione del servizio, che forse è opzionale
    temperature_patient_room_monitor_istnace.updateService()
    #while True :
    #    pass
