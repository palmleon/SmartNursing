from MyMQTT import *
import json
import requests
import time
class channelManager():
    def __init__(self,channelName='NewChannel'):
        self.channelName = channelName
        self.channelData = json.load(open('channelData.json'))
    def createChannel(self):
        requests.post('https://api.thingspeak.com/channels.json',json = self.channelData)
    def uploadToChannel(self,s):
        for i in range(len(s['e'])):
            field_t = s['e'][i]
            requests.get('https://api.thingspeak.com/update?api_key=VNU8XPP4S4XB4BJA&field{}={}'.format(i+1,field_t['v']))
            time.sleep(20)
    def channelFeed(self):
        r = requests.get('https://api.thingspeak.com/channels/1667352/feeds.json?api_key=R4I754QO2D02Z1OE&results=2')
        print(r.text)
        

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
        c = channelManager('test')
        #c.channelFeed()
        c.createChannel()
if __name__ == '__main__':
    tAdaptor = thinkSpeakAdaptor('ThinkSpeakAdaptor','dapis/test1','test.mosquitto.org',1883)
    tAdaptor.start()
    tAdaptor.subscribe(tAdaptor.topic)
    while True:
        time.sleep(1)
    tAdaptor.stop()
