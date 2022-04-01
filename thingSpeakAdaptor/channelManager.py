import json
import requests
import time


class channelManager():  # class for all methods related to ThingSpeak channels
    def __init__(self):
        self.channelData = json.load(open('channelData.json'))
        self.mainApiKey = self.channelData["api_key"]  # modify from catalogue
        self.channelList = []
        # self.conf_file = json.load(open('config.json'))
        # r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
        #     'serviceID' : 6,
        #     'name' : 'ThingSpeakAdapter'
        # }))

    def createChannel(self, cData=None):
        print('Adding new channel')
        if cData == None:
            cData = self.channelData
        if self.checkChannel(cData['name']) != 0:
            requests.post('https://api.thingspeak.com/channels.json', json=cData)
        else:
            print('Channel with the same name already present')
    
    def uploadToChannel(self,json_received): 
        channelToUpdate = self.checkChannel(json_received['bn'])
        print(channelToUpdate)
        if channelToUpdate == 0 or channelToUpdate == -1: #channel to update not present -> creation then update
            cData = self.channelData
            cData["name"] = json_received["bn"]
            for i in range(len(json_received['e'])):
                cData['field{}'.format(i+1)] = json_received['e'][i]['n']
            self.createChannel(cData)
            self.listChannels()
            self.uploadToChannel(json_received)
        else:
            write_api = channelToUpdate['api_keys'][0]['api_key']
            read_api = channelToUpdate['api_keys'][1]['api_key']
            channelID = channelToUpdate['id']
            #delta_t = json_received['bt']
            print('Upload in progress')
            for i in range(len(json_received['e'])):
                print('...')
                update_value = json_received['e'][i]
                field_number = self.channelFeed(channelID,read_api,update_value['n'])
                requests.get('https://api.thingspeak.com/update?api_key={}&field{}={}'.format(write_api,field_number,update_value['v']))
                time.sleep(16)
            print('Upload concluded')
            return 0
    
    def deleteChannel(self,channelID=None):  # delete a channel from a json dict
        if channelID!=None:
            print('Deleting channel {}'.format(channelID))
            if self.checkChannel(channelID) != 0:
                cID = self.retriveChannelID(channelID)
                print(cID)
                if cID != -1:
                    cData = self.channelData
                    cData['name'] == channelID
                    requests.delete('https://api.thingspeak.com/channels/{}.json'.format(cID), json=cData)
                    print('{} was deleted'.format(channelID))
            else:
                print('The provided channel does not exist')
        else:
            print('Deleting all channels')
            for i in range(0,len(self.channelList)):
                cData = self.channelData
                cData['name'] = self.channelList[i]['name']
                requests.delete('https://api.thingspeak.com/channels/{}.json'.format(self.channelList[i]['id']), json=cData)
            print('Delete Complete')

    
    def clearChannel(self, channelID = None):
        if channelID!=None:
            print('Clearing {} data'.format(channelID))
            if self.checkChannel(channelID) != 0:
                cID = self.retriveChannelID(channelID)
                if cID != -1:
                    cData = self.channelData
                    cData['name'] = channelID
                    requests.delete('https://api.thingspeak.com/channels/{}/feeds.json'.format(cID),json = cData)
                    print("{} 's fields cleared".format(channelID))
            else:
                print('The provided channel does not exist')
        else:
            print('Clearing all channel data')
            for i in range(0,len(self.channelList)):
                cData = self.channelData
                cData['name'] = self.channelList[i]['name']
                requests.delete('https://api.thingspeak.com/channels/{}/feeds.json'.format(self.channelList[i]['id']),json = cData)
            print('All channels fields cleared')
    
    def retriveChannelID(self,channelName):
        for i in range(0,len(self.channelList)):
            if self.channelList[i]['name'] == channelName:
                return self.channelList[i]['id']
        return -1
    
    
    
    def listChannels(self): #add to the list "channelList" all ThingSpeak channels with provided API
        thingSpeakList = requests.get('https://api.thingspeak.com/channels.json?api_key={}'.format(self.mainApiKey))
        thingSpeakList = json.loads(thingSpeakList.text)
        for i in range(len(thingSpeakList)):
            self.channelList.append(thingSpeakList[i])
    
    def checkChannel(self,channelID): #check if a channelID (in our case channel name) is present in channelList
        if len(self.channelList)>0:
            for channels in range(len(self.channelList)):
                print(self.channelList[channels]['name'])
                if channelID == self.channelList[channels]['name']:
                    return self.channelList[channels]
            return 0
        return -1
     
    def channelFeed(self,channelID,read_api,field_name): #retrive a chosen field number based on contents
        feed = requests.get('https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results=2'.format(channelID,read_api))
        feed = feed.json()
        feed = feed['channel']
        for i in range(1,9):
            if 'field{}'.format(i) in feed.keys():
                if feed['field{}'.format(i)] == field_name:
                    return i