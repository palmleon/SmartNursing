from calendar import c
from MyMQTT import *
from channelManager import *  
import threading

class thingSpeakAdaptor():
    """Class dedit to the interaction with ThingSpeak from MQTT messages"""
    def __init__(self):
        self.conf_file = json.load(open('config.json'))
        r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
            'serviceID' : 6,
            'name' : 'thingspeak-adaptor'
        }))
        if r.ok == False :
            print('Error adding the service')
        r = requests.get(self.conf_file['host']+"/message-broker")
        mb = r.json()
        self.clientID = 'ThingSpeakAdaptor'
        r = requests.get(self.conf_file['host']+"/patient-temperature-base-topic")
        self.topic=[]
        self.topic.append(r.json() + '+')
        r = requests.get(self.conf_file['host']+"/patient-saturation-base-topic")
        self.topic.append(r.json() + '+')
        self.client=MyMQTT(self.clientID,mb['name'],mb['port'],self,600)
        self.c = channelManager(self.conf_file['host'])
    def thingSpeakAdaptorSetUp(self):
        self.start()
        self.subscribe()
    def subscribe(self):
        for i in range (0,len(self.topic)):
            self.client.mySubscribe(self.topic[i])
    def stop(self):
        self.client.stop()
    def start (self):
        self.client.start()
    def notify(self,topic,msg):
        print('New data received')
        json_received = str(msg).replace("'",'"')
        json_received = json_received[2:-1]
        json_received = json.loads(json_received)
        self.c.cManager(json_received,topic)
    def updateService(self) :
        while True :
            time.sleep(100)
            r = requests.put(self.conf_file['host']+"/update-service",data = json.dumps({
                'serviceID' : 6,
                'name' : 'thingspeak-adaptor'
            }))
    def updatePatientList(self):
        while True:
            time.sleep(60*60)
            r = requests.get(self.conf_file['host']+"/patients")
            patients = r.json()
            self.c.updateList(patients)

if __name__ == '__main__':
    tAdaptor = thingSpeakAdaptor()
    tAdaptor.thingSpeakAdaptorSetUp()
    t1 = threading.Thread(target=tAdaptor.updatePatientList)
    t2 = threading.Thread(target=tAdaptor.updateService)
    t1.start()
    t2.start()
    t1.join()
    t2.join()
    tAdaptor.stop()
