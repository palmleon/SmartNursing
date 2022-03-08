from dataclasses import field
from MyMQTT import *
import json
import requests
import time

class thinkSpeakAdaptor():
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
        s = str(msg).replace("'",'"')
        s = s[2:-1]
        s = json.loads(s)
        self.uploadToChannel(s)
    def uploadToChannel(self,s):
        for fields in range(len(s['e'])):
            field = s['e'][fields]
            # requests here apparently works only the first time
            requests.get('https://api.thingspeak.com/update?api_key=VNU8XPP4S4XB4BJA&field{}={}'.format(fields+1,field['v']))
if __name__ == '__main__':
    tAdaptor = thinkSpeakAdaptor('ThinkSpeakAdaptor','dapis/test1','test.mosquitto.org',1883)
    tAdaptor.start()
    tAdaptor.subscribe(tAdaptor.topic)
    while True:
        time.sleep(1)
    tAdaptor.stop()
