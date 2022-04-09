from datetime import datetime
from matplotlib import pyplot
import json
from channelManager import *


class pythonPlotter():
    def __init__(self) -> None:
        self.apiKey = "YTN43QRA4IWIEBIN"
        self.temperature = []
        self.saturation = []
        self.pulseRate = []
        self.perfusionIndex = []
        self.label_map = ["battery oximeter", "perfusion index", "saturation",
                          "pulse rate", "battery termometer", "temperature", "day_flag"]

    def get(self, channelList):
        # Read all entries made in the last 24 hours. Returns a JSON.
        channelID = channelList[0]['id']
        read_api = channelList[0]['api_keys'][1]['api_key']
        r = requests.get(
            'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}'.format(channelID, read_api))
        data = json.loads(r.text)
        dic = dict()
        for i in range(len(self.label_map)):
            dic[self.label_map[i]] = []
        for feed in data.get('feeds'):
            for i in range(1, 8):
                if feed.get('field'+str(i)) is not None:
                    dic[self.label_map[i-1]].append(feed.get('field'+str(i)))
        return dic

    def checkValues(self, dic):
        for i in range(0, len(dic['temperature'])):
            if float(dic['temperature'][i]) < 38:
                dic['temperature'].remove(dic['temperature'][i])
        for i in range(0, len(dic['perfusion index'])):
            if float(dic['perfusion index'][i]) < 4:
                dic['perfusion index'].remove(dic['perfusion index'][i])
                dic['saturation'].remove(dic['perfusion index'][i])
                dic['pulse rate'].remove(dic['perfusion index'][i])
        return dic
    def calculateAverage(self,dic,measure):
        sum = 0
        count = 0
        for i in range(0,len(dic[measure])):
            sum = sum + float(dic[measure][i])
            count = count + 1
        return sum/count
    def dicToAvg(self,dic):
        for keys in dic.keys():
            if keys != 'battery oximeter' and keys != 'battery termometer' and keys!= 'day_flag':
                if dic[keys]:
                    dic[keys] = self.calculateAverage(dic,keys)
        return dic
    
    def plotter(self,dic):
        for keys in dic.keys():
            if keys != 'battery oximeter' and keys != 'battery termometer' and keys!= 'day_flag':
                if dic[keys]:
                    pyplot.scatter(datetime.fromtimestamp(time.time()),dic[keys])
        pyplot.show()





if __name__ == '__main__':
    plot = pythonPlotter()
    c = channelManager()
    c.listChannels()
    v = plot.get(c.channelList)
    v = plot.checkValues(v)
    v = plot.dicToAvg(v)
    plot.plotter(v)
    # # x-axis values
    # roll_num = [1, 2, 3, 4, 5, 6, 7, 8, 9]

    # # y-axis values
    # marks = [55, 75, 96, 75, 36, 45, 87, 99, 100]


    # pyplot.scatter(roll_num,datetime.fromtimestamp(time.time()))


    # pyplot.show()
