from MyMQTT import *
from channelManager import *
from datetime import datetime
        

class thinkSpeakAdaptor(): #class related to the interaction with MQTT 
    def __init__(self,clientID,topic,broker,port):
        self.topic=topic
        self.client=MyMQTT(clientID,broker,port,self)
    def subscribe(self,topic):
        self.client.mySubscribe(topic)
    def stop(self):
        self.client.stop()
    def start (self):
        self.client.start()
    def notify(self,topic,msg):
        print('New data received')
        c = channelManager()
        c.listChannels()
        json_received = str(msg).replace("'",'"')
        json_received = json_received[2:-1]
        json_received = json.loads(json_received)
        if topic == 'dapis/test1':
            c.uploadToChannel(json_received)
        elif topic == 'dapis/maintainance': #in case we want channel creation via mqtt
            print('maintanance')
            #print(c.channelList)
            c.deleteChannel(json_received['bn'])
            #c.clearChannel('ID Paziente 1')
            

if __name__ == '__main__':
    tAdaptor = thinkSpeakAdaptor('ThinkSpeakAdaptor','dapis/test1','test.mosquitto.org',1883)
    tAdaptor.start()
    tAdaptor.subscribe(tAdaptor.topic)
    tAdaptor.subscribe('dapis/maintainance')
    while True:
        time.sleep(1)
    tAdaptor.stop()
