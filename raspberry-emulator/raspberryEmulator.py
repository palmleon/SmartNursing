import time
import requests
import threading
import signal
from MyMQTT import *
from lightSensor import *
from temperatureAndMotionSensor import *
from patientTemperatureSensor import *
from patientOximeterSensor import *
import json
class RaspberryEmulator :

  

    def __init__(self) :
        self.__fp = open('config.json')
        self.__patientRooms = {}
        self.__commonRooms = []
        self.__conf_file = json.load(self.__fp)
        self.sampleNumber = int(self.__conf_file['oximeter-sample-number'])
        self.lightSensor = LightSensor(self.__conf_file['room-light-sensor-base-message'])
        self.temperatureRoomSensor = TemperatureAndMotionRoomSensor(self.__conf_file['room-temperature-motion-sensor-base-message'])
        self.patientOximeterSensor = Oximeter_sensor(self.__conf_file['oximeter-sensor-base-message'],self.sampleNumber)
        self.patientTemperatureSensor = Temperature_sensor(self.__conf_file['patient-temperature-sensor-base-message'])
        self.__patientOximeterEmulatorIntervalMinute = self.__conf_file['patientOximeterEmulatorIntervalMinute']
        self.__patientTemperatureEmulatorIntervalMinute = self.__conf_file['patientTemperatureEmulatorIntervalMinute']
        self.__patientLightRoomEmulatorIntervalMinute = self.__conf_file['patientLightRoomEmulatorIntervalMinute']
        self.__patientTemperatureRoomEmulatorIntervalMinute = self.__conf_file['patientTemperatureRoomEmulatorIntervalMinute']
        self.__commonRoomEmulatorIntervalMinute = self.__conf_file['commonRoomEmulatorIntervalMinute']
        self.__updateIntervalMinute = self.__conf_file['updateIntervalMinute']
        self.patientSensorsList = self.__conf_file["patient_sensors"]
        self.commonRoomSensorsList = self.__conf_file["common_room_sensors"]
        self.patientRoomSensorsList = self.__conf_file["patient-room-sensors"]
        self.__fp.close()
        try:
            r = requests.get(self.__conf_file['host']+"/message-broker")
            mb = r.json()
            self.__mqttClient = MyMQTT('raspberry-emulator',mb['name'],mb['port'],self)
            r = requests.get(self.__conf_file['host']+"/patient-room-light-command-base-topic")
            c = r.json()  
            self.__patientRoomLightCommandTopic = c
            r = requests.get(self.__conf_file['host']+"/patient-room-temperature-command-base-topic")
            c = r.json()  
            self.__patientRoomTemperatureCommandTopic = c
            r = requests.get(self.__conf_file['host']+"/common-room-command-base-topic")
            c = r.json()
            self.__commonRoomCommandTopic = c 
            
            r = requests.get(self.__conf_file['host']+"/patient-room-temperature-base-topic")
            c = r.json()
            self.__patientTemperatureRoomTopic = c
            r = requests.get(self.__conf_file['host']+"/patient-room-light-base-topic")
            c = r.json()
            self.__patientLightRoomTopic = c
            r = requests.get(self.__conf_file['host']+"/common-room-base-topic")
            c = r.json()
            self.__commonRoomTopic = c
            r = requests.get(self.__conf_file['host']+"/patient-saturation-base-topic")
            c = r.json()
            self.__patientSaturationTopic = c
            r = requests.get(self.__conf_file['host']+"/patient-temperature-base-topic")
            c = r.json()
            self.__patientTemperatureTopic = c
        except:
            print("ERROR: init fails, restart the container")
        
        self.__mqttClient.start()
        self.__mqttClient.mySubscribe(self.__commonRoomCommandTopic)
        self.__mqttClient.mySubscribe(self.__patientRoomTemperatureCommandTopic)
        self.__mqttClient.mySubscribe(self.__patientRoomLightCommandTopic)

        


    def notify(self,topic,payload) :
        command = dict(json.loads(payload))
        #self.fp = open("actuation_command.json","a")
        #json.dump(command,self.fp)
        #self.fp.close()
        room = topic.split("/")[-1]
        print('Actuation command for room' +room+' received: '+str(command)) 

    def emulateCommonRoomData(self) :
        while True :
            time.sleep(self.__commonRoomEmulatorIntervalMinute*60)
            for room in self.__commonRooms :
                dataEmulated = self.temperatureRoomSensor.emulateData(room)
                self.__mqttClient.myPublish(self.__commonRoomTopic+str(room),dataEmulated)
                #print("simulo per stanza ",room["roomID"]," al seguente topic ",self.__commonRoomTopic+str(room["roomID"]))
                #print("stanza emulata "+str(self.roomSensor.emulateData(room)))

    def emulatePatientRoomTemperatureData(self) :
        while True :
            time.sleep(self.__patientTemperatureRoomEmulatorIntervalMinute*60)
            #print("simulo per le seguenti stanze ",str(list(self.__patientRooms.keys())))
            for room in list(self.__patientRooms.keys()) :
                if len(self.__patientRooms[room]) != 0 :
                    #self.roomEmulator.emulateData()
                    #fare publish
                    dataEmulated = self.temperatureRoomSensor.emulateData(room)
                    self.__mqttClient.myPublish(self.__patientTemperatureRoomTopic+str(room),dataEmulated)
                    #print("simulo per stanza ",room," al seguente topic ",self.patientRoomTopic+str(room))
    def emulatePatientRoomLightData(self) :
        while True :
            time.sleep(self.__patientLightRoomEmulatorIntervalMinute*60)
            #print("simulo per le seguenti stanze ",str(list(self.__patientRooms.keys())))
            for room in list(self.__patientRooms.keys()) :
                if len(self.__patientRooms[room]) != 0 :
                    #self.roomEmulator.emulateData()
                    #fare publish
                    dataEmulated = self.lightSensor.emulateData(room)
                    self.__mqttClient.myPublish(self.__patientLightRoomTopic+str(room),dataEmulated)
                    #print("simulo per stanza ",room," al seguente topic ",self.patientRoomTopic+str(room))
                    
    def emulatePatientSaturationData(self) :
        while True :
            time.sleep(self.__patientOximeterEmulatorIntervalMinute*60) 
            for room in list(self.__patientRooms.keys()) :
                for id in self.__patientRooms[room] :
                    dataEmulated = self.patientOximeterSensor.emulate(id)
                    self.__mqttClient.myPublish(self.__patientSaturationTopic+str(id),dataEmulated)
                    #print("simulo Pulsossimetro per paziente ",id," al seguente topic ",self.__patientSaturationTopic+str(id))
    
    def emulatePatientTemperatureData(self) :
        while True :
            time.sleep(self.__patientTemperatureEmulatorIntervalMinute*60)
            for room in list(self.__patientRooms.keys()) :
                for id in self.__patientRooms[room] :
                    dataEmulated = self.patientTemperatureSensor.emulate(id)
                    self.__mqttClient.myPublish(self.__patientTemperatureTopic+str(id),dataEmulated)
                    #print("simulo temperatura per paziente ",id," al seguente topic ",self.__patientTemperatureTopic+str(id))
            
    def updateServices(self) :
        while True :
            time.sleep(self.__updateIntervalMinute*60)
            for commonRoom in self.__commonRooms :
                for sensor in self.commonRoomSensorsList :
                    try :

                        r = requests.post(self.__conf_file['host']+"/add-device",data = json.dumps({
                                                                        'deviceID' : str(commonRoom)+sensor,
                                                                        'name' : sensor}))
                        if r.ok != True :
                            print("ERROR: update common room device failed")
                    except :
                        print("ERROR: update common room device failed")
                    
            for room in list(self.__patientRooms.keys()) :
                if len(self.__patientRooms[room]) != 0:
                    for sensor in self.patientRoomSensorsList :
                        try :
                            r = requests.post(self.__conf_file['host']+"/add-device",data = json.dumps({
                                                                            'deviceID' : str(room)+sensor,
                                                                            'name' : sensor
                                                                        }))
                            if r.ok != True :
                                print("ERROR: update patient room device failed")
                        except :
                            print("ERROR: update patient room device failed")

                    
                    
                    for id in self.__patientRooms[room] :
                        for sensor in self.patientSensorsList :
                            try :
                                r = requests.post(self.__conf_file['host']+"/add-device",data = json.dumps({
                                                                                    'deviceID' : str(id)+sensor,
                                                                                    'patientID' : int(id),
                                                                                    'name' : sensor}))
                                if r.ok != True :
                                    print("ERROR: update patient device failed")
                            except :
                                print("ERROR: update patient device fails")
            
    def listenUserCommand(self) :
        choice = int(input("\nEnter 1 to add a patient, 0 to remove a patient, 2 to add a common room, 3 to remove a common room, 4 to exit "))
        #lanciare thread che registra i device relativi a stanze e pazienti
    
        while choice != 4 :
            room = 0
            patientId = 0
            if choice == 1 :
                patientId = int(input("Insert patient's id "))
                roomId = int(input("Insert room number "))

                if roomId in self.__patientRooms :
                    if patientId not in self.__patientRooms[roomId] :
                        self.__patientRooms[roomId].append(patientId)
                        for sensor in self.patientSensorsList :
                            try :
                                r = requests.post(self.__conf_file['host']+"/add-device",data = json.dumps({
                                                                                    'deviceID' : str(patientId)+sensor,
                                                                                    'patientID' : int(patientId),
                                                                                    'name' : sensor}))
                                if r.ok != True :
                                    print("ERROR: add patient room device fails")
                            except :
                                print("ERROR: add patient room device fails")
            
                        
                else :
                    print(self.patientSensorsList)
                    print(self.patientRoomSensorsList)
                    print(self.commonRoomSensorsList)
                    self.__patientRooms[roomId] = [patientId]
                    for sensor in self.patientRoomSensorsList :
                        try :
                            r = requests.post(self.__conf_file['host']+"/add-device",data = json.dumps({
                                                                            'deviceID' : str(roomId)+sensor,
                                                                            'name' : sensor
                                                                        }))
                            if r.ok != True :
                                    print("ERROR: add patient room device fails")
                        except :
                            print("ERROR: add patient room device fails")
                    
                    for sensor in self.patientSensorsList :
                        try:

                            r = requests.post(self.__conf_file['host']+"/add-device",data = json.dumps({
                                                                                    'deviceID' : str(patientId)+sensor,
                                                                                    'patientID' : int(patientId),
                                                                                    'name' : sensor
                }))     
                            if r.ok != True :
                                print("ERROR: add patient  device fails")
                        except :
                            print("ERROR: add patient  device fails")
            if choice == 0 :
                patientId = int(input("Insert the id of the patient to remove "))
                for room in list(self.__patientRooms.keys()) :
                    for id in self.__patientRooms[room] :
                        if id == patientId :
                            self.__patientRooms[room].remove(id)
            print(self.__patientRooms)
            if choice == 2 :
                found = False
                roomID = int(input("Insert common room id to add "))
                #check che non esiste
                for room in self.__commonRooms :
                    if room == roomID :
                        found = True
                if found == False :
                    self.__commonRooms.append(roomID)
                    for sensor in self.commonRoomSensorsList :
                        try :

                            r = requests.post(self.__conf_file['host']+"/add-device",data = json.dumps({
                                                                                'deviceID' : str(roomID)+sensor,
                                                                                'name' : sensor}))
                            if r.ok != True :
                                    print("ERROR: add commmon room device fails")
                        except :
                            print("ERROR: add common room device fails")

                print(self.__commonRooms)
            if choice == 3 :
                found = False
                roomID = int(input("Insert common room id to remove "))
                for room in self.__commonRooms :
                    if room == roomID :
                        found = True
                if found == True :
                    self.__commonRooms.remove(roomID)

                print(self.__commonRooms)
                        
                
            choice = int(input("\nEnter 1 to add a patient, 0 to remove a patient, 2 to add a common room, 3 to remove a common room, 4 to exit "))

def alarm_handler(signum, frame):
    raise TimeoutError

def input_with_timeout(timeout):
    signal.signal(signal.SIGALRM, alarm_handler) # the lambda is only used to raise an Exception in case the timer expires
    signal.alarm(timeout) # produce SIGALRM in `timeout` seconds 
    reply = None
    try:
        reply = input("\rPress enter to start: ")
    except TimeoutError:
        pass
    finally:
        signal.alarm(0) # cancel alarm
        if reply != None:
            return False
        else:
            return True

if __name__ == "__main__" : 

    # Timed input to start the raspberry emulator
    timer_active = True
    while timer_active:
        timer_active = input_with_timeout(5)

    e = RaspberryEmulator()
    t1 = threading.Thread(target=e.updateServices)
    t2 = threading.Thread(target=e.emulateCommonRoomData)
    t3 = threading.Thread(target=e.emulatePatientSaturationData)
    t4 = threading.Thread(target=e.emulatePatientRoomTemperatureData)
    t5 = threading.Thread(target=e.listenUserCommand)
    t6 = threading.Thread(target=e.emulatePatientTemperatureData)
    t7 = threading.Thread(target=e.emulatePatientRoomLightData)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    t7.start()
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    t7.join()
    
    
