from datetime import datetime
from os import times
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
        self.labelOfInterests = ['temperature', 'saturation', 'pulse rate']

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

    def retriveDatesData(self, dic, patientID, measure):
        dataList = []
        for i in range(0, len(dic)):
            if dic[i]['channelID'] == patientID:
                if len(dic[i][measure]) > 0:
                    for j in range(0, len(dic[i][measure])):
                        for key in dic[i][measure][j].keys():
                            dataList.append(key)
        return dataList

    def getPatientsData(self, dic, patientID, measure, date):
        chosenDataList = []
        for i in range(0, len(dic)):
            if dic[i]['channelID'] == patientID:
                if len(dic[i][measure]) > 0:
                    for j in range(0, len(dic[i][measure])):
                        if date in dic[i][measure][j].keys():
                            chosenDataList.append(dic[i][measure][j][date])
        return chosenDataList

    def tempAverage(self, temperatureList):
        sum = 0
        counter = 0
        if temperatureList is not None:
            if len(temperatureList) > 0:
                for i in range(0, len(temperatureList)):
                    if float(temperatureList[i]) > 35:
                        sum = sum + float(temperatureList[i])
                        counter = counter + 1
                if counter != 0:
                    avg = sum/counter
                    return avg

    def piAverage(self, perfusionIndex, saturation, pulseRate):
        sumSat = 0
        sumPulse = 0
        counter = 0
        if saturation is not None and perfusionIndex is not None and pulseRate is not None:
            if len(perfusionIndex) > 0 and len(saturation) > 0 and len(pulseRate) > 0:
                for i in range(0, len(perfusionIndex)):
                    if float(perfusionIndex[i]) > 4:
                        if i < len(saturation) and i < len(pulseRate):
                            sumSat = sumSat + float(saturation[i])
                            sumPulse = sumPulse + float(pulseRate[i])
                            counter = counter + 1
                avgSaturation = sumSat/counter
                avgPulse = sumPulse/counter
                return avgSaturation, avgPulse

    def removeDuplicates(self, duplicatedlist):
        notDuplicatedList = []
        for i in range(len(duplicatedlist)):
            if duplicatedlist[i] not in notDuplicatedList:
                notDuplicatedList.append(duplicatedlist[i])
        return notDuplicatedList

    def performForAllMeasures(self,dic):
        avgTempDic = dict()
        avgSaturationDic = dict()
        avgPulseDic = dict()
        tempDates = dict()
        satDates = dict()
        pulseDates = dict()
        for i in range(0,len(dic)):
            temperatureDates = plot.retriveDatesData(dic, dic[i]['channelID'], 'temperature')
            temperatureDates = plot.removeDuplicates(temperatureDates)
            saturationDates = plot.retriveDatesData(dic, dic[i]['channelID'], 'saturation')
            saturationDates = plot.removeDuplicates(saturationDates)
            pulseRateDates = plot.retriveDatesData(dic, dic[i]['channelID'], 'pulse rate')
            pulseRateDates = plot.removeDuplicates(pulseRateDates)
            piDates = plot.retriveDatesData(dic, dic[i]['channelID'], 'perfusion index')
            piDates = plot.removeDuplicates(piDates)
            tempDates[dic[i]['channelID']] = temperatureDates
            satDates[dic[i]['channelID']] = saturationDates
            pulseDates[dic[i]['channelID']] = pulseRateDates
            avgTemp = []
            for j in range(0, len(temperatureDates)):
                temperature = plot.getPatientsData(dic, dic[i]['channelID'], 'temperature', temperatureDates[j])
                avgTemp.append(plot.tempAverage(temperature))
            avgTempDic[dic[i]['channelID']] = avgTemp
            avgSat = []
            avgPulse = []
            for j in range(0,len(piDates)):
                saturation = plot.getPatientsData(dic, dic[i]['channelID'], 'saturation', piDates[j])
                pulseRate = plot.getPatientsData(dic, dic[i]['channelID'], 'pulse rate', piDates[j])
                pi = plot.getPatientsData(dic, dic[i]['channelID'], 'perfusion index', piDates[j])
                if pulseRate is not None and saturation is not None and pi is not None:
                    if len(pulseRate) > 0 and len(saturation) > 0 and len(pi)>0 :
                        avgSaturation,avgPulseRate = plot.piAverage(pi,saturation,pulseRate)
                        avgSat.append(avgSaturation)
                        avgPulse.append(avgPulseRate)
            if avgSat is not None and avgPulse is not None:
                avgSaturationDic[dic[i]['channelID']] = avgSat
                avgPulseDic[dic[i]['channelID']] = avgPulse
        self.plotter(avgTempDic,avgSaturationDic,avgPulseDic,tempDates,satDates,pulseDates,len(dic))
    
    def saveToJson(self, dic):
        json.dump(dic, open('test.json', 'w'))
    

    def plotter(self, temperature, saturation, pulseRate, timeTemp, timeSat, timePulse, patientNumber):
        j = 0
        for i in range(0,patientNumber):
            keyT = list(timeTemp.keys())
            keyS = list(timeSat.keys())
            keyP = list(timePulse.keys())
            pyplot.subplot(patientNumber, 3, j+1)
            pyplot.scatter(timeTemp[keyT[i]], temperature[keyT[i]])
            pyplot.subplot(patientNumber, 3, j+2)
            pyplot.scatter(timeSat[keyS[i]], saturation[keyS[i]])
            pyplot.subplot(patientNumber, 3, j+3)
            pyplot.scatter(timePulse[keyP[i]], pulseRate[keyP[i]])
            j = j + 1
        pyplot.show()


if __name__ == '__main__':
    plot = pythonPlotter()
    c = channelManager()
    c.listChannels()
    v = plot.retriveLatestData(c.channelList)
    plot.saveToJson(v)
    d = datetime.fromtimestamp(time.time())
    d = d.replace(d.year, d.month, 13)  # d.day - 1)
    d = str(d).split(' ')[0]
    plot.performForAllMeasures(v)
