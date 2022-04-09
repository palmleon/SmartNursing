from re import I
import requests
import json
from channelManager import *

class pythonPlotter():
    def __init__(self) -> None:
        self.apiKey = json.load(open('channelData.json'))['api_key']
        self.temperature = []
        self.saturation = []
        self.pulseRate = []
        self.perfusionIndex = []
        self.label_map = ["battery oximeter","perfusion index","saturation","pulse rate","battery termometer","temperature","day_flag"]

    def get(self,channelList):
        #Read all entries made in the last 24 hours. Returns a JSON.
        channelID = channelList[0]['id']
        read_api = channelList[0]['api_keys'][1]['api_key']
        r = requests.get('https://api.thingspeak.com/channels/{}/feeds.json?api_key={}'.format(channelID,read_api))       
        data = json.loads(r.text)
        dic = dict()
        for i in range(len(self.label_map)):
            dic[self.label_map[i]] = []
        for feed in data.get('feeds'):
            for i in range(1,8):
                if feed.get('field'+str(i)) is not None:
                    dic[self.label_map[i-1]].append(feed.get('field'+str(i)))
        return dic
    def checkValues(self,dic):
        print(len(dic['temperature']))
        for i in range(0,len(dic['temperature'])):
            print(dic['temperature'][0])
            if float(dic['temperature'][i]) < 38 :
                dic['temperature'].remove(dic['temperature'][i])
        print(dic)
if __name__ == '__main__':
    plot = pythonPlotter()
    c = channelManager()
    c.listChannels()
    v = plot.get(c.channelList)
    plot.checkValues(v)