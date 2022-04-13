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
        self.label_map = ["battery oximeter", "perfusion index", "saturation","pulse rate", "battery termometer", "temperature", "day_flag"]
        self.labelOfInterests = ['temperature','saturation','pulse rate']

    def retriveLatestData(self, channelList):
        today = datetime.fromtimestamp(time.time()).day
        dataList = []
        for j in range(0, len(channelList)):
            channelID = channelList[j]['id']
            read_api = channelList[j]['api_keys'][1]['api_key']
            r = requests.get(
                'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}'.format(channelID, read_api))
            data = json.loads(r.text)
            dic = dict()
            dic['channelID'] = data['channel']['name']
            for i in range(len(self.label_map)):
                dic[self.label_map[i]] = []
            for feed in data.get('feeds'):
                dateReceived = feed.get('created_at')
                date = dateReceived.split('-')[0] + '-' + dateReceived.split(
                    '-')[1] + '-' + dateReceived.split('-')[2].split('T')[0]
                for i in range(1, 8):
                    if feed.get('field'+str(i)) is not None:
                        newDict = dict()
                        newDict[date] = feed.get('field'+str(i))
                        dic[self.label_map[i-1]].append(newDict)
            dataList.append(dic)
        return dataList

    def getPatientsData(self,dic,patientID,measure,date):
        chosenDataList = []
        for i in range(0,len(dic)):
            if dic[i]['channelID'] == patientID:
                if len(dic[i][measure]) > 0:
                    for j in range(0,len(dic[i][measure])):
                        if date in dic[i][measure][j].keys():
                            chosenDataList.append(dic[i][measure][j][date])
        return chosenDataList

    def getValuesFromKey(self,dic,key,measure):
        for items in range(0,len(dic)):
            if len(dic[items][measure]) > 0:
                for i in range(0,len(dic[items][measure])):
                    print(dic[items][measure][i])
                    if key in dic[items][measure][i].keys():
                        print(dic[items][measure][i][key])
                        print(dic[items]['channelID'])

    def calculateAverage(self,l):
        sum = 0
        if l is not None:
            if len(l) > 0:
                for i in range(0,len(l)):
                    if float(l[i]) > 35:
                        sum  = sum + float(l[i])
                avg = sum/len(l)
                return avg
    
    def dataOfInterest(self,dic):
        pass

    def saveToJson(self,dic):
        json.dump(dic,open('test.json','w'))
    def plotter(self,dic):
        for keys in dic.keys():
            if dic[keys]:
                pyplot.scatter(datetime.fromtimestamp(time.time()).day,dic[keys])
        pyplot.show()
        self.saveToJson(dic)


if __name__ == '__main__':
    plot = pythonPlotter()
    c = channelManager()
    c.listChannels()
    v = plot.retriveLatestData(c.channelList)
    plot.saveToJson(v)
    d = datetime.fromtimestamp(time.time())
    d = d.replace(d.year,d.month,13)#d.day - 1)
    d = str(d).split(' ')[0]
    l = plot.getPatientsData(v,'5','temperature',d)
    print(l)
    print(plot.calculateAverage(l))
    #plot.calculateAverage(v,'temperature')