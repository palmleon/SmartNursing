from MyMQTT import *
import json
import requests
import time
class channelManager(): #class for all methods related to ThingSpeak channels
    def __init__(self):
        self.channelData = json.load(open('channelData.json'))
        self.mainApiKey = self.channelData["api_key"] #modify from catalogue
        self.channelList = []
        # self.conf_file = json.load(open('config.json'))
        # r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
        #     'serviceID' : 6,
        #     'name' : 'ThingSpeakAdapter'
        # }))
    def createChannel(self,cData = None): #create a ThingSpeak channel from channelData.json
        print('Adding new channel')
        if cData == None:
            cData = self.channelData
        if self.checkChannel(cData['name']) == 0:
            requests.post('https://api.thingspeak.com/channels.json',json = cData)
        else:
            print('Channel with the same name already present')
    def deleteChannel(self,cData = None): #delete a channel from a json dict
        print('Deleting channel')
        if cData == None:
            cData = self.channelData
        if self.checkChannel(cData['name']) == 0:
            requests.delete('https://api.thingspeak.com/channels.json',json = cData)
        else:
            print('The provided channel does not exist')
    def listChannels(self): #add to the list "channelList" all ThingSpeak channels with provided API
        thingSpeakList = requests.get('https://api.thingspeak.com/channels.json?api_key={}'.format(self.mainApiKey))
        thingSpeakList = json.loads(thingSpeakList.text)
        for i in range(len(thingSpeakList)):
            self.channelList.append(thingSpeakList[i])
    def checkChannel(self,channelID): #check if a channelID (in our case channel name) is present in channelList
        for channels in range(len(self.channelList)):
            if channelID == self.channelList[channels]['name']:
                return self.channelList[channels]
        return 0
    #upload channel based on json received (channel name) and field (json content)
    #if bn not in channelList createChannel and then upload
    def uploadToChannel(self,json_received): 
        channelToUpdate = self.checkChannel(json_received['bn'])
        if channelToUpdate != 0:
            write_api = channelToUpdate['api_keys'][0]['api_key']
            read_api = channelToUpdate['api_keys'][1]['api_key']
            channelID = channelToUpdate['id']
            print('Upload in progress')
            for i in range(len(json_received['e'])):
                print('...')
                update_value = json_received['e'][i]
                field_number = self.channelFeed(channelID,read_api,update_value['n'])
                requests.get('https://api.thingspeak.com/update?api_key={}&field{}={}'.format(write_api,field_number,update_value['v']))
                time.sleep(16)
            print('Upload concluded')
        else:
            cData = self.channelData
            cData["name"] = json_received["bn"]
            for i in range(len(json_received['e'])):
                cData['field{}'.format(i+1)] = json_received['e'][i]['n']
            self.createChannel(cData)
            self.uploadToChannel(json_received)
    def channelFeed(self,channelID,read_api,field_name): #retrive a chosen field number based on contents
        feed = requests.get('https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results=2'.format(channelID,read_api))
        feed = feed.json()
        feed = feed['channel']
        for i in range(1,9):
            if 'field{}'.format(i) in feed.keys():
                if feed['field{}'.format(i)] == field_name:
                    return i
        

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
