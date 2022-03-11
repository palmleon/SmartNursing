from asyncore import read
from MyMQTT import *
import json
import requests
import time
class channelManager():
    def __init__(self):
        self.channelData = json.load(open('channelData.json'))
        self.mainApiKey = self.channelData["api_key"]
        self.channelList = []
    def createChannel(self):
        print('Adding new channel')
        if self.checkChannel(self.channelData['name']) == 0:
            requests.post('https://api.thingspeak.com/channels.json',json = self.channelData)
        else:
            print('Channel with the same name already present')
    def listChannels(self):
        thingSpeakList = requests.get('https://api.thingspeak.com/channels.json?api_key={}'.format(self.mainApiKey))
        thingSpeakList = json.loads(thingSpeakList.text)
        for i in range(len(thingSpeakList)):
            self.channelList.append(thingSpeakList[i])
    def checkChannel(self,channelID):
        for channels in range(len(self.channelList)):
            if channelID == self.channelList[channels]['name']:
                return self.channelList[channels]
        return 0
    def uploadToChannel(self,json_received):
        channelToUpdate = self.checkChannel(json_received['bn'])
        write_api = channelToUpdate['api_keys'][0]['api_key']
        read_api = channelToUpdate['api_keys'][1]['api_key']
        channelID = channelToUpdate['id']
        if channelToUpdate != 0:
            print('Upload in progress')
            for i in range(len(json_received['e'])):
                print('...')
                update_value = json_received['e'][i]
                field_number = self.channelFeed(channelID,read_api,update_value['n'])
                requests.get('https://api.thingspeak.com/update?api_key={}&field{}={}'.format(write_api,field_number,update_value['v']))
                time.sleep(20)
            print('Upload concluded')
    def channelFeed(self,channelID,read_api,field_name):
        feed = requests.get('https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results=2'.format(channelID,read_api))
        feed = feed.json()
        feed = feed['channel']
        for i in range(1,9):
            if 'field{}'.format(i) in feed.keys():
                if feed['field{}'.format(i)] == field_name:
                    return i
        

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
        print('New data received')
        c = channelManager()
        c.listChannels()
        if topic == 'dapis/test1':
            json_received = str(msg).replace("'",'"')
            json_received = json_received[2:-1]
            json_received = json.loads(json_received)
            c.uploadToChannel(json_received)
        elif topic == 'dapis/maintainance': #in case we want channel creation via mqtt
            print('maintanance')
            c.createChannel()
            

if __name__ == '__main__':
    tAdaptor = thinkSpeakAdaptor('ThinkSpeakAdaptor','dapis/test1','test.mosquitto.org',1883)
    tAdaptor.start()
    tAdaptor.subscribe(tAdaptor.topic)
    tAdaptor.subscribe('dapis/maintainance')
    while True:
        time.sleep(1)
    tAdaptor.stop()
