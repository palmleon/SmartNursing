import json
import requests
import time

class channelManager():
    """Class containing all methods related to ThingSpeak channels"""
    def __init__(self):
        """Init\n
        channelData -> default ThingSpeak channel configuration\n
        mainApiKey -> ThingSpeak account API\n
        channelList -> local list of ThingSpeak channels"""
        self.channelData = json.load(open('channelData.json'))
        self.mainApiKey = self.channelData["api_key"]
        self.channelList = []
    
    def listChannels(self):
        """All ThingSpeak channels will be added to the local channel list with rest API"""
        thingSpeakList = requests.get('https://api.thingspeak.com/channels.json?api_key={}'.format(self.mainApiKey))
        thingSpeakList = json.loads(thingSpeakList.text)
        for i in range(len(thingSpeakList)):
            self.channelList.append(thingSpeakList[i])
    
    def isChannelinList(self,channelID):
        """ Checks if a channel is present in the ThingSpeak channels list\n
        Parameters
        ----------
        channelID: str
            Name of the channel to be checked
        
        Returns
        -------
        The channel if it has been found\n
        0 if the channel is not present in the channel list
        """
        if len(self.channelList) > 0:
            for i in range(0,len(self.channelList)):
                if self.channelList[i]['name'] == channelID:
                    return self.channelList[i]
        return 0
    
    def createChannel(self,cJson):
        """Creates a new ThingSpeak channel with rest API\n
        If no paramater is given it will create a channel with the default configuration\n
        Parameters
        ----------
        cJata: dict
            dictionary containing all the data of the channel to be added
        """
        cData = self.channelData
        if cJson == None:
            print('Adding new channel with default configuration')
            requests.post('https://api.thingspeak.com/channels.json', json=cData)
        else:
            cData['name'] = cJson['bn']
            print('Adding {} as a new channel'.format(cData['name']))
            if self.isChannelinList(cData['name']) == 0:
                requests.post('https://api.thingspeak.com/channels.json', json=cData)
                self.listChannels()
            else:
                print('This channel already exists!')

    def cManager(self,cJson):
        """Channel creations and updates manager\n
        Parameters
        ----------
        cJson: dict
            dict containing data"""
        self.listChannels()
        if self.isChannelinList(cJson['bn']) == 0:
            self.createChannel(cJson)
        self.channelUpdater(cJson)

    def channelFeed(self,channelID,read_api,field_name,len):
        """Retrive a chosen field number based on contents\n
        Parameters
        ----------
        channelID: str
            Name of the channel we are working with
        read_api: str
            ThingSpeak read API
        field_name: str
            Name of the field we use to find the corresponding index
        len: int
            length of the payload dict containing data (2 or 4)
            
        Returns
        -------
            Field Number: int (1-8)"""
        feed = requests.get('https://api.thingspeak.com/channels/{}/feeds.json?api_key={}&results=2'.format(channelID,read_api))
        feed = feed.json()
        feed = feed['channel']
        for i in range(1,9):
            if 'field{}'.format(i) in feed.keys():
                if feed['field{}'.format(i)] == field_name:
                    return i
                if field_name == 'battery':
                    if len == 2:
                        return 5
                    elif len == 4:
                        return 1

    def channelUpdater(self,cJson):
        """Updates channel with new data\n
        Parameters
        ----------
        cJson: dict"""
        channelToUpdate = self.isChannelinList(cJson['bn'])
        write_api = channelToUpdate['api_keys'][0]['api_key']
        read_api = channelToUpdate['api_keys'][1]['api_key']
        channelID = channelToUpdate['id']
        print('Upload in progress')
        for i in range(len(cJson['e'])):
            update_value = cJson['e'][i]
            field_number = self.channelFeed(channelID,read_api,update_value['n'],len(cJson['e']))
            if type(update_value['v']) == list:
                for i in range(0,len(update_value['v'])):
                    print('...')
                    requests.get('https://api.thingspeak.com/update?api_key={}&field{}={}'.format(write_api,field_number,update_value['v'][i]))
                    time.sleep(16)
            else:
                print('...')
                requests.get('https://api.thingspeak.com/update?api_key={}&field{}={}'.format(write_api,field_number,update_value['v']))
                time.sleep(16)
        print('Upload concluded')
        
    def deleteChannel(self,channelID=None):
        """Delete a channel\n
        if the channelID is not specified it will delete all channels\n
        Parameters
        ----------
        channelID: str"""
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
        """Clear channel all channel field\n
        if the channelID is not specified it will clear all channels fields\n
        Parameters
        ----------
        channelID: str"""
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
        """From channel name retrive channel ID\n
        Parameters
        ----------
        channelName: str
        
        Returns
        --------
        channelID: int if the channel name is present in the channel list\n
        -1 if it is not present"""
        for i in range(0,len(self.channelList)):
            if self.channelList[i]['name'] == channelName:
                return self.channelList[i]['id']
        return -1