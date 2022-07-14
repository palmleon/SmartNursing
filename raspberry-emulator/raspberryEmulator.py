import time
import requests
import threading
import signal
from MyMQTT import *
from lightSensor import *
from temperatureSensor import *
from patientTemperatureSensor import *
from patientOximeterSensor import *
import json
class RaspberryEmulator :

  

    def __init__(self) :
        
        self.rooms = {}
        self.lightSensor = LightSensor()
        self.temperatureRoomSensor = TemperatureRoomSensor()
        self.patientOximeterSensor = Oximeter_sensor()
        self.patientTemperatureSensor = Temperature_sensor()
        self.conf_file = json.load(open('config.json'))
        self.patientMonitorEmulatorIntervalMinute = self.conf_file['patientMonitorEmulatorIntervalMinute']
        self.patientTemperatureEmulatorIntervalMinute = self.conf_file['patientTemperatureEmulatorIntervalMinute']
        self.patientLightRoomEmulatorIntervalMinute = self.conf_file['patientLightRoomEmulatorIntervalMinute']
        self.patientTemperatureRoomEmulatorIntervalMinute = self.conf_file['patientTemperatureRoomEmulatorIntervalMinute']
        self.commonRoomEmulatorIntervalMinute = self.conf_file['commonRoomEmulatorIntervalMinute']
        self.updateIntervalMinute = self.conf_file['updateIntervalMinute']
        r = requests.get(self.conf_file['host']+"/message-broker")
        mb = r.json()
        self.mqttClient = MyMQTT('raspberry-emulator',mb['name'],mb['port'],self)
        r = requests.get(self.conf_file['host']+"/patient-room-command-base-topic")
        c = r.json()  
        self.patientRoomCommandTopic = c
        r = requests.get(self.conf_file['host']+"/common-room-command-base-topic")
        c = r.json()
        self.commonRoomCommandTopic = c 
        r = requests.get(self.conf_file['host']+"/common-room-list")
        c = r.json()
        self.commonRoomList = c
        r = requests.get(self.conf_file['host']+"/patient-room-temperature-base-topic")
        c = r.json()
        self.patientTemperatureRoomTopic = c
        r = requests.get(self.conf_file['host']+"/patient-room-light-base-topic")
        c = r.json()
        self.patientLightRoomTopic = c
        r = requests.get(self.conf_file['host']+"/common-room-base-topic")
        c = r.json()
        self.commonRoomTopic = c
        r = requests.get(self.conf_file['host']+"/patient-saturation-base-topic")
        c = r.json()
        self.patientSaturationTopic = c
        r = requests.get(self.conf_file['host']+"/patient-temperature-base-topic")
        c = r.json()
        self.patientTemperatureTopic = c
        self.mqttClient.start()
        self.mqttClient.mySubscribe(self.commonRoomCommandTopic)
        self.mqttClient.mySubscribe(self.patientRoomCommandTopic)
        for room in self.commonRoomList :
             r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                    'deviceID' : str(room["roomID"])+'tc',
                                                                    'name' : 'common-room-temperature'
        }))

    def notify(self,topic,payload) :
        command = dict(json.loads(payload))
        #self.fp = open("actuation_command.json","a")
        #json.dump(command,self.fp)
        #self.fp.close()
        print('Actuation command received: '+str(command)) 

    def emulateCommonRoomData(self) :
        while True :
            time.sleep(self.commonRoomEmulatorIntervalMinute*60)
            for room in self.commonRoomList :
                dataEmulated = self.temperatureRoomSensor.emulateData(room["roomID"])
                self.mqttClient.myPublish(self.commonRoomTopic+str(room["roomID"]),dataEmulated)
                #print("simulo per stanza ",room["roomID"]," al seguente topic ",self.commonRoomTopic+str(room["roomID"]))
                #print("stanza emulata "+str(self.roomSensor.emulateData(room)))

    def emulatePatientRoomTemperatureData(self) :
        while True :
            time.sleep(self.patientTemperatureRoomEmulatorIntervalMinute*60)
            #print("simulo per le seguenti stanze ",str(list(self.rooms.keys())))
            for room in list(self.rooms.keys()) :
                if len(self.rooms[room]) != 0 :
                    #self.roomEmulator.emulateData()
                    #fare publish
                    dataEmulated = self.temperatureRoomSensor.emulateData(room)
                    print('pubblico temperasturas per stanza paziente',dataEmulated)
                    self.mqttClient.myPublish(self.patientTemperatureRoomTopic+str(room),dataEmulated)
                    #print("simulo per stanza ",room," al seguente topic ",self.patientRoomTopic+str(room))
    def emulatePatientRoomLightData(self) :
        while True :
            time.sleep(self.patientLightRoomEmulatorIntervalMinute*60)
            #print("simulo per le seguenti stanze ",str(list(self.rooms.keys())))
            for room in list(self.rooms.keys()) :
                if len(self.rooms[room]) != 0 :
                    #self.roomEmulator.emulateData()
                    #fare publish
                    dataEmulated = self.lightSensor.emulateData(room)
                    self.mqttClient.myPublish(self.patientLightRoomTopic+str(room),dataEmulated)
                    #print("simulo per stanza ",room," al seguente topic ",self.patientRoomTopic+str(room))
                    
    def emulatePatientSaturationData(self) :
        while True :
            time.sleep(self.patientMonitorEmulatorIntervalMinute*60) 
            for room in list(self.rooms.keys()) :
                for id in self.rooms[room] :
                    dataEmulated = self.patientOximeterSensor.emulate(id)
                    self.mqttClient.myPublish(self.patientSaturationTopic+str(id),dataEmulated)
                    #print("simulo Pulsossimetro per paziente ",id," al seguente topic ",self.patientSaturationTopic+str(id))
    
    def emulatePatientTemperatureData(self) :
        while True :
            time.sleep(self.patientTemperatureEmulatorIntervalMinute*60)
            for room in list(self.rooms.keys()) :
                for id in self.rooms[room] :
                    dataEmulated = self.patientTemperatureSensor.emulate(id)
                    self.mqttClient.myPublish(self.patientTemperatureTopic+str(id),dataEmulated)
                    #print("simulo temperatura per paziente ",id," al seguente topic ",self.patientTemperatureTopic+str(id))
            
    def updateServices(self) :
        while True :
            time.sleep(self.updateIntervalMinute*60)
            for commonRoom in self.commonRoomList :
                r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : str(commonRoom["roomID"])+'tc',
                            'name' : 'common-room-temperature'
                        }))

            for room in list(self.rooms.keys()) :
                if len(self.rooms[room]) != 0:
                    r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : str(room)+'p',
                            'name' : 'room-presence-sensor'
                        }))
                    r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : str(room)+'t',
                            'name' : 'room-temperature-sensor'
                        }))
                    r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : str(room)+'l',
                            'name' : 'room-light-sensor'
                        }))
                    for id in self.rooms[room] :
                        r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : str(id)+'tp',
                            'patientID' : int(id),
                            'name' : 'patient-temperature-sensor'
                        }))
                        r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : str(id)+'o',
                            'patientID' : int(id),
                            'name' : 'patient-oximeter-sensor'

                        }))
            
    def listenUserCommand(self) :
        choice = int(input("Enter 1 to add a patient, 0 to remove a patient, 2 to exit "))
        #lanciare thread che registra i device relativi a stanze e pazienti
    
        while choice != 2 :
            room = 0
            patientId = 0
            if choice == 1 :
                patientId = int(input("Insert patient's id "))
                roomId = int(input("Insert room number "))

                if roomId in self.rooms :
                    if patientId not in self.rooms[roomId] :
                        self.rooms[roomId].append(patientId)
                        r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                            'deviceID' : str(patientId)+'tp',
                                                                            'patientID' : int(patientId),
                                                                            'name' : 'patient-temperature-sensor'
        }))
                        r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                                            'deviceID' : str(patientId)+'o',
                                                                                            'patientID' : int(patientId),
                                                                                            'name' : 'patient-oximeter-sensor'
        }))
                else :
                    self.rooms[roomId] = [patientId]
                    r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                        'deviceID' : str(roomId)+'p',
                                                                        'name' : 'room-presence-sensor'
                                                                    }))
                    r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                        'deviceID' : str(roomId)+'l',
                                                                        'name' : 'room-light-sensor'
                                                                    }))
                    r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                        'deviceID' : str(roomId)+'t',
                                                                        'name' : 'room-temperature-sensor'
                                                                    }))
                    
                    r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                            'deviceID' : str(patientId)+'tp',
                                                                            'patientID' : int(patientId),
                                                                            'name' : 'patient-temperature-sensor'
        }))
                    r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                                            'deviceID' : str(patientId)+'o',
                                                                                            'patientID' : int(patientId),
                                                                                            'name' : 'patient-oximeter-sensor'
        }))
            if choice == 0 :
                patientId = int(input("Insert the id of the patient to remove "))
                for room in list(self.rooms.keys()) :
                    for id in self.rooms[room] :
                        if id == patientId :
                            self.rooms[room].remove(id)
            print(self.rooms)
            choice = int(input("Enter 1 to add a patient, 0 to remove a patient, 2 to exit "))

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
    
    
