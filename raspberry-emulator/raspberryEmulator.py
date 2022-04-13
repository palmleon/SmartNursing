import time
import requests
import threading
from MyMQTT import *
from roomSensor import *
from patientTemperatureSensor import *
from patientOximeterSensor import *
import json
class RaspberryEmulator :

    patientMonitorEmulatorIntervalMinute = 0.5
    patientTemperatureEmulatorIntervalMinute = 1
    patientRoomEmulatorIntervalMinute = 2
    commonRoomEmulatorIntervalMinute = 1
    updateIntervalMinute = 3

    def __init__(self) :
        self.patientMonitorEmulatorIntervalMinute = 0.5
        self.patientTemperatureEmulatorIntervalMinute = 1
        self.patientRoomEmulatorIntervalMinute = 2
        self.commonRoomEmulatorIntervalMinute = 1
        self.updateIntervalMinute = 3
        self.rooms = {}
        self.roomSensor = RoomSensor()
        self.patientOximeterSensor = Oximeter_sensor()
        self.patientTemperatureSensor = Temperature_sensor()
        self.conf_file = json.load(open('config.json'))
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
        print('stanze comuni',r.json()) 
        r = requests.get(self.conf_file['host']+"/patient-room-base-topic")
        c = r.json()
        self.patientRoomTopic = c
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
                                                                    'deviceID' : room,
                                                                    'name' : 'light-patient-room-monitor'
        }))

    def notify(self,topic,payload) :
        command = dict(json.loads(payload))
        self.fp = open("actuation_command.json","a")
        json.dump(command,self.fp)
        self.fp.close()
        print('ricevuto comando')#rimuovere 

    def emulateCommonRoomData(self) :
        while True :
            time.sleep(self.commonRoomEmulatorIntervalMinute*60)
            for room in self.commonRoomList :
                dataEmulated = self.roomSensor.emulateData(room)
                self.mqttClient.myPublish(self.commonRoomTopic+str(room),dataEmulated)
                print("simulo per stanza ",room," al seguente topic ",self.commonRoomTopic+str(room))
                #print("stanza emulata "+str(self.roomSensor.emulateData(room)))

    def emulatePatientRoomData(self) :
        while True :
            time.sleep(self.patientRoomEmulatorIntervalMinute*60)
            print("simulo per le seguenti stanze ",str(list(self.rooms.keys())))
            for room in list(self.rooms.keys()) :
                if len(self.rooms[room]) != 0 :
                    #self.roomEmulator.emulateData()
                    #fare publish
                    dataEmulated = self.roomSensor.emulateData(room)
                    self.mqttClient.myPublish(self.patientRoomTopic+str(room),dataEmulated)
                    print("simulo per stanza ",room," al seguente topic ",self.patientRoomTopic+str(room))
                    
    def emulatePatientSaturationData(self) :
        while True :
            time.sleep(self.patientMonitorEmulatorIntervalMinute*60) 
            for room in list(self.rooms.keys()) :
                for id in self.rooms[room] :
                    dataEmulated = self.patientOximeterSensor.emulate(id)
                    self.mqttClient.myPublish(self.patientSaturationTopic+str(id),dataEmulated)
                    print("simulo ossimetro per paziente ",id," al seguente topic ",self.patientSaturationTopic+str(id))
    
    def emulatePatientTemperatureData(self) :
        while True :
            time.sleep(self.patientTemperatureEmulatorIntervalMinute)
            for room in list(self.rooms.keys()) :
                for id in self.rooms[room] :
                    dataEmulated = self.patientTemperatureSensor.emulate(id)
                    self.mqttClient.myPublish(self.patientTemperatureTopic+str(id),dataEmulated)
                    print("simulo temperatura per paziente ",id," al seguente topic ",self.patientTemperatureTopic+str(id))
            
    def updateServices(self) :
        while True :
            time.sleep(self.updateIntervalMinute*60)
            for commonRoom in self.commonRoomList :
                r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : commonRoom,
                            'name' : 'patient-room-device-'+id
                        }))

            for room in list(self.rooms.keys()) :
                if len(self.rooms[room]) != 0:
                    r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : id,
                            'name' : 'patient-room-device-'+id
                        }))
                    for id in self.rooms[room] :
                        r = requests.put(self.conf_file['host']+"/update-device",data = json.dumps({
                            'deviceID' : id,
                            'name' : 'patient-device-'+id
                        }))
            
    def listenUserCommand(self) :
        choice = int(input("Inserisci 1 per aggiungere paziente, 0 per rimuovere paziente, 2 per terminare "))
        #lanciare thread che registra i device relativi a stanze e pazienti
    
        while choice != 2 :
            room = 0
            patientId = 0
            if choice == 1 :
                patientId = int(input("Inserisci id paziente da aggiungere "))
                roomId = int(input("Inserisci numero stanza "))

                if roomId in self.rooms :
                    if patientId not in self.rooms[roomId] :
                        self.rooms[roomId].append(patientId)
                        r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                            'deviceID' : patientId,
                                                                            'name' : 'light-patient-room-monitor'
        }))
                else :
                    self.rooms[roomId] = [patientId]
                    r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                        'deviceID' : roomId,
                                                                        'name' : 'light-patient-room-monitor'
                                                                    }))
                    r = requests.post(self.conf_file['host']+"/add-device",data = json.dumps({
                                                                    'deviceID' : patientId,
                                                                    'name' : 'light-patient-room-monitor'
        }))
            if choice == 0 :
                patientId = int(input("Inserisci id paziente da rimuvere "))
                for room in list(self.rooms.keys()) :
                    for id in self.rooms[room] :
                        if id == patientId :
                            self.rooms[room].remove(id)
            print(self.rooms)
            choice = int(input("Inserisci 1 per aggiungere paziente, 0 per rimuovere paziente, 2 per terminare "))

if __name__ == "__main__" : 
    e = RaspberryEmulator()
    t1 = threading.Thread(target=e.listenUserCommand)
    t2 = threading.Thread(target=e.emulateCommonRoomData)
    t3 = threading.Thread(target=e.emulatePatientSaturationData)
    t4 = threading.Thread(target=e.emulatePatientRoomData)
    t5 = threading.Thread(target=e.updateServices)
    t6 = threading.Thread(target=e.emulatePatientTemperatureData)

    t1.start()
    t2.start()
    t3.start()
    t4.start()
    t5.start()
    t6.start()
    
    t1.join()
    t2.join()
    t3.join()
    t4.join()
    t5.join()
    t6.join()
    
    
    
