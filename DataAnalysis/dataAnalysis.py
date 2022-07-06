import json
from channelManager import *
import requests
from datetime import date
from datetime import datetime


class dataAnalysis():
    def __init__(self):
        self.conf_file = json.load(open('config.json'))
        r = requests.post(self.conf_file['host']+"/add-service",data =json.dumps( {
            'serviceID' : 8,
            'name' : 'data-analysis'
        }))
        r = requests.get(self.conf_file['host']+"/channel-data")
        self.fields = r.json()
        r = requests.get(self.conf_file['host']+"/patient-room-hourly-scheduling")
        r = r.json()
        self.timeInterval = r['night']
        self.timeInterval = [18,22] ######### TEST #######
        self.watingTime = 60*2
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
        print('Uploading ' + stringField)
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
    def strUTC2(self,date):
        bhour = date['hour']
        bday = date['day']
        bmonth = date['month']
        if bhour == '00':
            date['hoour'] == '02'
            date['day'] == str(int(date['day']) + 1)
            if bmonth == '11' or bmonth == '06' or bmonth =='04' or bmonth =='09':
                if bday == '30':
                    date['day'] == '01'
                    date['month'] == str(int(date['month']) + 1)
            elif bmonth == '02':
                if bday == '28':
                    date['day'] == '01'
                    date['month'] == str(int(date['month']) + 1)
            elif bmonth == '01' or bmonth == '03' or bmonth == '05' or \
                bmonth == '07' or bmonth == '08' or bmonth == '10' or \
                bmonth == '12':
                if bday == '31':
                    date['day'] == '01'
                    date['month'] == str(int(date['month']) + 1)
            if bmonth == '12' and bday == '31':
                date['year'] == str(int(date['year']) + 1)
        else:
            date['hour'] = str(int(date['hour']) + 2)
        return date
    def convertData(self,stringDate):
        date = dict()
        date['year'] = stringDate[0:4]
        date['month'] = stringDate[5:7]
        date['day'] = stringDate[8:10]
        date['hour'] = str(int(stringDate[11:13]))
        date['minutes'] = stringDate[14:16]
        date['seconds'] = stringDate[17:19]
        date = self.strUTC2(date)
        return date
    def checkDate(self,dicData):
        today = date.today()
        print(dicData)
        if int(dicData['year']) == today.year:
            print('year')
            if int(dicData['month']) == today.month:
                print('month')
                if int(dicData['day']) == today.day - 1:
                    print('day1')
                    if int(dicData['hour']) >= self.timeInterval[0]:
                        print('hour1')
                        return True
                elif int(dicData['day']) == today.day:
                    print('day2')
                    if int(dicData['hour']) <= self.timeInterval[1]:
                        print('hour2')
                        return True
            elif int(dicData['month']) == today.month - 1:
                if int(dicData['hour']) >= self.timeInterval[0]:
                    return True
                elif int(dicData['day']) == today.day:
                    if int(dicData['hour']) <= self.timeInterval[1]:
                        return True
        return False   
    def averageTemp(self,temperatureList):
        print('Calculating Average Temperature')
        sum = 0
        count = 0
        if len(temperatureList) >= 1:
            for i in range(0,len(temperatureList)):
                if float(temperatureList[i]) >= 35:
                    sum = sum + float(temperatureList[i])
                    count = count + 1
            if count != 0:
                print(sum/count)
                return sum/count
            else:
                return 0
        else:
            return None
    def averagePi(self,pi,saturation,pulse):
        print('Calculating Averate Pulse rate and Saturation')
        sumSat = 0
        countSat = 0
        countPulse = 0
        sumPulse = 0
        if len(pi) >= 1:
            if len(saturation) >= 1:
                if len(pulse) >= 1:
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
                    print('avgSat: ' + str(avgSat) + '  avgPulse: ' + str(avgPulse))
                    return avgPulse,avgSat
        return None,None
def perform():
    conf_file = json.load(open('config.json'))
    c = channelManager(conf_file['host'])
    d = dataAnalysis()
    flag_time = 1
    print('Starting data analysis')
    lastTimeExec = datetime.fromtimestamp(time.time())
    lastTimeExec = d.convertData(str(lastTimeExec))
    while True:
        now = datetime.fromtimestamp(time.time())
        now = d.convertData(str(now))
        print('LastTimeExec: ' + lastTimeExec['hour']+':'+lastTimeExec['minutes']+':'+\
            lastTimeExec['seconds']+'  '+lastTimeExec['day']+'/'+lastTimeExec['month']+'/'+\
                lastTimeExec['year'])
        print('Now: ' + now['hour']+':'+now['minutes']+':'+\
            now['seconds']+'  '+now['day']+'/'+now['month']+'/'+\
                now['year'])
        if lastTimeExec != 0:
            if int(now['day']) > int(lastTimeExec['day']):
                if int(now['hour']) >= d.timeInterval[1]:
                    if int(now['hour']) <= d.timeInterval[0]:
                        flag_time = 1
                        lastTimeExec = now
                        print('A day has passed, time to check data\n')
            else:
                flag_time = 0
        count = 0 ########### TEST ########
        if count == 0: ########### TEST ########
            flag_time = 1 ########### TEST ########
            count = 1 ########### TEST ########
        if flag_time == 1:
            c.listChannels()
            if len(c.channelList) > 0:
                latestDate = d.retriveData(c.channelList)
                for keys in latestDate.keys():
                    tempList = []
                    piList = []
                    satList = []
                    pulseList = []
                    temperature = None
                    pulse = None
                    saturation = None
                    print('Checking patient ' + str(keys) + ' data')
                    for i in range(0,len(latestDate[keys])):
                        check = d.checkDate(d.convertData(\
                            latestDate[keys][i]['created_at']))
                        #check = True ########## TEST ###########
                        print(check)
                        if check == True:
                            if latestDate[keys][i]['field5'] != None:
                                tempList.append(latestDate[keys][i]['field5'])
                            if latestDate[keys][i]['field7'] != None:
                                piList.append(latestDate[keys][i]['field7'])
                            if latestDate[keys][i]['field1'] != None:
                                satList.append(latestDate[keys][i]['field1'])
                            if latestDate[keys][i]['field3'] != None:
                                pulseList.append(latestDate[keys][i]['field3'])
                    if len(tempList) >= 1:
                        temperature = d.averageTemp(tempList)
                    if len(piList) >= 1:
                        if len(satList) >= 1:
                            if len(pulseList) >= 1:
                                pulse,saturation = d.averagePi(piList,satList,pulseList)
                    if temperature != None:
                        d.uploadAVG(keys,c.channelList,temperature,'average temperature')
                    if pulse != None:
                        d.uploadAVG(keys,c.channelList,pulse,'average pulse rate')
                    if saturation != None:
                        d.uploadAVG(keys,c.channelList,saturation,'average saturation')
                    print('\n')
        print('Repeating check after ' + str(d.watingTime) + ' minutes')
        time.sleep(d.watingTime)
        
if __name__ == '__main__':
    perform()

    