from collections import defaultdict
import json
from channelManager import *
import requests
import cherrypy



class dataPlotter():
    def __init__(self) -> None:
        self.conf_file = json.load(open('config.json'))
        self.thingspeakMeasures = ["battery oximeter", "perfusion index", "saturation",
                          "pulse rate", "battery termometer", "temperature", "day_flag"]
        self.measureOfInterest = ["perfusion index", "saturation","pulse rate","temperature"]
        # r = requests.post(self.conf_file['host']+"/add-service", data=json.dumps({
        #     'serviceID': 22,
        #     'name': 'data-plotter'
        # }))
        # if r.ok == False:
        #     print('Error adding the service')
    def retriveLatestData(self, channelList):
        """Retrive all data from thingspeak\n
        Parameters
        ----------
        channelList: list
            local list containing all thingspeak channels
        Returns
        -------
        dataList: list
            a list of dictionaries containing all latest data"""
        dataList = []
        for j in range(0, len(channelList)):
            channelID = channelList[j]['id']
            read_api = channelList[j]['api_keys'][1]['api_key']
            r = requests.get(
                'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}'.format(channelID, read_api))
            data = json.loads(r.text)
            dic = dict()
            dic['channelID'] = data['channel']['name']
            for i in range(len(self.thingspeakMeasures)):
                dic[self.thingspeakMeasures[i]] = []
            for feed in data.get('feeds'):
                dateReceived = feed.get('created_at')
                date = dateReceived.split('-')[0] + '-' + dateReceived.split(
                    '-')[1] + '-' + dateReceived.split('-')[2].split('T')[0]
                for i in range(1, 8):
                    if feed.get('field'+str(i)) is not None:
                        newDict = dict()
                        newDict[date] = feed.get('field'+str(i))
                        dic[self.thingspeakMeasures[i-1]].append(newDict)
            dataList.append(dic)
        return dataList

    def removeBatteryData(self,list):
        for i in range(0,len(list)):
            if "battery oximeter" in list[i].keys():
                list[i].pop("battery oximeter")
            if "battery termometer" in list[i].keys():
                list[i].pop("battery termometer")
        return list

    def allDates(self,list):
        l = []
        for i in range(0,len(list)):
            for m in self.measureOfInterest:
                for j in range(0,len(list[i][m])):
                    for k in list[i][m][j].keys():
                        l.append(k)
        l = self.removeDuplicates(l)
        return l
    
    def removeDuplicates(self,list):
        newList = []
        for i in range(0,len(list)):
            if list[i] not in newList:
                newList.append(list[i])
        return newList

    def temperatureAverage(self,list,patient,date):
        temp = 0
        count = 0
        for i in range(0,len(list)):
            if list[i]['channelID'] == patient:
                for j in range(0,len(list[i]['temperature'])):
                    if date in list[i]['temperature'][j].keys():
                        if float(list[i]['temperature'][j][date]) >= 35:
                            temp = temp + float(list[i]['temperature'][j][date])
                            count = count + 1
        if count > 0:
            return temp/count
        return 0
    
    def piAverage(self,list,patient,date):
        sat = 0
        pulse = 0
        countSat = 0
        countPulse = 0
        for i in range(0,len(list)):
            if list[i]['channelID'] == patient:
                leng = len(list[i]['perfusion index'])
                if leng > len(list[i]['saturation']) or leng > len(list[i]['pulse rate']):
                    if len(list[i]['saturation']) > len(list[i]['pulse rate']):
                        leng = len(list[i]['pulse rate'])
                    else:
                        leng = len(list[i]['saturation'])
                for j in range(0,leng):
                    if date in list[i]['perfusion index'][j].keys():
                        if float(list[i]['perfusion index'][j][date]) > 4:
                            if date in list[i]['saturation'][j].keys():
                                sat = sat + float(list[i]['saturation'][j][date])
                                countSat = countSat + 1
                            if date in list[i]['pulse rate'][j].keys():
                                pulse = pulse + float(list[i]['pulse rate'][j][date])
                                countPulse = countPulse + 1
        if countPulse > 0:
            avgPulse = pulse/countPulse
        else:
            avgPulse = 0
        if countSat > 0:
            avgSat = sat/countSat
        else:
            avgSat = 0
        return avgPulse,avgSat
    
    def calcAverage(self,list,date):
        d = defaultdict(dict)
        for i in range(0,len(list)):
            for j in range(0,len(date)):
                d[list[i]['channelID']][date[j]] = self.temperatureAverage(list,list[i]['channelID'],date[j])
        avgTemp = d
        d = defaultdict(dict)
        e = defaultdict(dict)
        for i in range(0,len(list)):
            for j in range(0,len(date)):
                d[list[i]['channelID']][date[j]],e[list[i]['channelID']][date[j]] = self.piAverage(list,list[i]['channelID'],date[j])
        avgPulse = d
        avgSat = e
        return avgTemp,avgPulse,avgSat

    def saveToJson(self, dic):
        json.dump(dic, open('averageData.json', 'w'))
    def retriveID(self,list):
        ids = []
        for i in range(0,len(list)):
            ids.append(list[i]['id'])
        return ids

def performID():
    plot = dataPlotter()
    c = channelManager()
    c.listChannels()
    ids = plot.retriveID(c.channelList)
    return ids

def perform():
    plot = dataPlotter()
    c = channelManager()
    c.listChannels()
    latestData = plot.retriveLatestData(c.channelList)
    latestData = plot.removeBatteryData(latestData)
    listDate = plot.allDates(latestData)
    avgTemp,avgPulse,avgSat = plot.calcAverage(latestData,listDate)
    d = dict()
    d['temperature'] = avgTemp
    d['pulse rate'] = avgPulse
    d['saturation'] = avgSat
    plot.saveToJson(d)

class rest():
    exposed = True
    def __init__(self) -> None:
        pass
    def GET(self,*uri):
        perform()
        if len(uri) > 0:
            s = str(uri)
            s = s.replace('(','').replace(',','').replace(')','').replace("'",'')
            if s == 'id':
                return json.dumps(performID())
        perform()
        f = open('averageData.json')
        d = json.load(f)
        return json.dumps(d)


if __name__ == '__main__':
    conf = {
        '/': {
                'request.dispatch': cherrypy.dispatch.MethodDispatcher(),
                'tool.session.on': True
        }
    }
    cherrypy.tree.mount(rest(), '/', conf)
    cherrypy.engine.start()
    cherrypy.engine.block()





