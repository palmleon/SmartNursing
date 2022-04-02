from MyMQTT import *
from channelManager import *        

class thinkSpeakAdaptor():
    """Class dedit to the interaction with ThingSpeak from MQTT messages"""
    def __init__(self):
        self.clientID = 'ThingSpeakAdaptor'
        self.broker = 'test.mosquitto.org'
        self.topic='dapis/test1'
        self.port = 1883
        self.client=MyMQTT(self.clientID,self.broker,self.port,self)
    def subscribe(self,topic):
        self.client.mySubscribe(topic)
    def stop(self):
        self.client.stop()
    def start (self):
        self.client.start()
    def notify(self,topic,msg):
        print('New data received')
        c = channelManager()
        json_received = str(msg).replace("'",'"')
        json_received = json_received[2:-1]
        json_received = json.loads(json_received)
        if topic == 'dapis/test1':
           c.cManager(json_received)
            

if __name__ == '__main__':
    tAdaptor = thinkSpeakAdaptor()
    tAdaptor.start()
    tAdaptor.subscribe(tAdaptor.topic)
    tAdaptor.subscribe('dapis/maintainance')
    while True:
        time.sleep(1)
    tAdaptor.stop()
