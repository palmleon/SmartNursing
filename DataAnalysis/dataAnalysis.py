import json
from channelManager import *
import requests
from datetime import date


class dataAnalysis():
    def __init__(self):
        self.conf_file = json.load(open('config.json'))
        r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
            'serviceID' : 8,
            'name' : 'data-analysis'
        }))
        r = requests.get(self.conf_file['host']+"/channel-data")
        self.fields = r.json()
        # self.fields = {'field1':'average saturation',
        # 'field2': 'perfusion index', 
        # 'field3': 'saturation', 
        # 'field4':'pulse rate', 
        # 'field5':'average pulse rate', 
        # 'field6': 'temperature', 
        # 'field7': 'average temperature', 
        # 'field8': 'day_flag'}
        r = requests.get(self.conf_file['host']+"/patient-room-hourly-scheduling")
        r = r.json()
        self.timeInterval = r['night']
    def retriveData(self,channelList):
        dataDict = dict()
        for i in range(0,len(channelList)):
            channelID = channelList[i]['id']
            read_api = channelList[i]['api_keys'][1]['api_key']
            r = requests.get(
                'https://api.thingspeak.com/channels/{}/feeds.json?api_key={}'.format(channelID, read_api))
            data = r.json()
            dataDict[data['channel']['name']] = data['feeds']
        return dataDict
    def uploadAVG(self,channelID,channelList,avgdata,stringField):
        print('Upload in progress')
        for i in range(0,len(channelList)):
            if channelList[i]['name'] == channelID:
                write_api = channelList[i]['api_keys'][0]['api_key']
                read_api = channelList[i]['api_keys'][1]['api_key']
                if stringField in self.fields.values():
                    field_number = int(str(self.get_key(stringField,self.fields)).replace('field',''))
                    requests.get('https://api.thingspeak.com/update?api_key={}&field{}={}'.format(
                            write_api, field_number,avgdata))
                    print('...')
                    time.sleep(16)
        print('Upload concluded')
    def get_key(self,val,dic):
        for key, value in dic.items():
            if val == value:
                return key
    def convertData(self,stringDate):
        date = dict()
        date['year'] = stringDate[0:4]
        date['month'] = stringDate[5:7]
        date['day'] = stringDate[8:10]
        date['hour'] = str(int(stringDate[11:13]) + 2)
        date['minutes'] = stringDate[14:16]
        date['seconds'] = stringDate[17:19]
        return date
    def checkDate(self,dicData):
        today = date.today()
        if dicData['year'] == str(today.year):
            if dicData['month'] == str(today.month):
                if dicData['day'] == str(today.day - 1):
                    if dicData['hour'] >= '21':
                        return True
                elif dicData['day'] == str(today.day):
                    if dicData['hour'] <= '10':
                        return True
        return False   
    def averageTemp(self,temperatureList):
        sum = 0
        count = 0
        for i in range(0,len(temperatureList)):
            if float(temperatureList[i]) >= 35:
                sum = sum + float(temperatureList[i])
                count = count + 1
                print(temperatureList[i],sum,count)
        if count != 0:
            print(sum/count)
            return sum/count
        else:
            return 0
    def averagePi(self,pi,saturation,pulse):
        sumSat = 0
        countSat = 0
        countPulse = 0
        sumPulse = 0
        if len(pi) >= len(saturation) or len(pi) >= len(pulse):
            if len(saturation) >= len(pulse):
                l = len(pulse)
            else:
                l = len(saturation)
        else:
            l = len(pi)
        for i in range(0,l):
            if float(pi[i]) >= 4:
                sumSat = sumSat + float(saturation[i])
                countSat = countSat + 1
                sumPulse = sumPulse + float(pulse[i])
                countPulse = countPulse + 1
        if countSat !=0:
            avgSat = sumSat/countSat
        else:
            avgSat = 0
        if countPulse !=0:
            avgPulse = sumPulse/countPulse
        else:
            avgPulse = 0
        return avgPulse,avgSat
def perform():
    conf_file = json.load(open('config.json'))
    c = channelManager(conf_file['host'])
    d = dataAnalysis()
    c.listChannels()
    latestDate = d.retriveData(c.channelList)
    for keys in latestDate.keys():
        tempList = []
        piList = []
        satList = []
        pulseList = []
        for i in range(0,len(latestDate[keys])):
            check = d.checkDate(d.convertData(\
                latestDate[keys][i]['created_at']))
            check = True ########## TEST ###########
            if check == True:
                if latestDate[keys][i]['field6'] != None:
                    tempList.append(latestDate[keys][i]['field6'])
                if latestDate[keys][i]['field2'] != None:
                    piList.append(latestDate[keys][i]['field2'])
                if latestDate[keys][i]['field3'] != None:
                    satList.append(latestDate[keys][i]['field3'])
                if latestDate[keys][i]['field4'] != None:
                    pulseList.append(latestDate[keys][i]['field4'])
        temperature = d.averageTemp(tempList)
        pulse,saturation = d.averagePi(piList,satList,pulseList)
        d.uploadAVG(keys,c.channelList,temperature,'average temperature')
        d.uploadAVG(keys,c.channelList,pulse,'average pulse rate')
        d.uploadAVG(keys,c.channelList,saturation,'average saturation')


if __name__ == '__main__':
    perform()

    