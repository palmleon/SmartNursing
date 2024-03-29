import json
import cherrypy
import time
import datetime

class Catalog(object) :
    exposed = True
    def __init__(self) :
        self.conf_file = json.load(open('config.json'))
        self.refreshCatalogIntervalMinute = int(self.conf_file['refreshCatalogIntervalMinute'])
        
        try : 
            self.fp = open("/usr/app/catalog.json","r")
            self.catalogList = json.load(self.fp)
        except:
            self.fp = open("catalog.json","r")
            self.catalogList = json.load(self.fp)
        self.catalogList['services'] = []
        self.fp.close()
        
    #compute the differences in minutes to determine which services or devices are not updated
    def computeDifference(self,t2,t1) :
        t1 = datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S.%f")
        diff = t2-t1
        diff = diff.total_seconds()
        return diff/60

    #refresh the catalog, deleting services and devices not updated
    def refreshList(self) :
        while True :
            time.sleep(60*self.refreshCatalogIntervalMinute)
            #Delete devices and services not updated
            self.catalogList['devices'] = list(filter(lambda dev : self.computeDifference(datetime.datetime.today(),dev['timestamp']) < 2,self.catalogList['devices']))
            self.catalogList['services'] = list(filter(lambda dev : self.computeDifference(datetime.datetime.today(),dev['timestamp']) < 2,self.catalogList['services']))
            self.fp = open("/usr/app/catalog.json","w")
            json.dump(self.catalogList,self.fp)
            self.fp.close()

    def GET(self,*uri):
        if len(uri) == 0 :
            raise cherrypy.HTTPError(400,'Wrong parameters number')

        if uri[0] == 'message-broker' :
            return json.dumps(self.catalogList["message-broker"])
        elif uri[0] == 'channel-data' :
            return json.dumps(self.catalogList["channel-data"])
        elif uri[0] == 'city' :
            return json.dumps(self.catalogList['city'])
        elif uri[0] == 'api-weather' :
            return json.dumps(self.catalogList['api-weather'])
        elif uri[0] == 'bot-token' :
            return json.dumps(self.catalogList['bot-token'])
        
        elif uri[0] == 'telegram-user-id-list' :
            return json.dumps(self.catalogList['telegram-user-id-list'])

        elif uri[0] == 'telegram-tasks' :
            return json.dumps(self.catalogList['telegram-tasks'])

        elif uri[0] == 'telegram-task' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'telegram task missing')
            for task in self.catalogList['telegram-tasks'] :
                if task['command'] == uri[1] :
                    return json.dumps(task)
            raise cherrypy.HTTPError(400,'telegram task not found')

        elif uri[0] == 'common-room-temperature':
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'roomID missing')
            for room in self.catalogList['common-room-list'] :
                if room['roomID'] == int(uri[1]) :
                    return json.dumps({"desired-temperature" : room['desired-temperature']})
            raise cherrypy.HTTPError(400,'room not found')

        elif uri[0] == 'room-temperature' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'roomID missing')
            for room in self.catalogList['room-list'] :
                if room['roomID'] == int(uri[1]) :
                    return json.dumps({"desired-temperature" : room['desired-temperature']})
            raise cherrypy.HTTPError(400,'room not found')
        
        elif uri[0] == 'room-list' :
            return json.dumps(self.catalogList['room-list'])

        elif uri[0] == 'common-room-list' :
            return json.dumps(self.catalogList['common-room-list'])
        
        elif uri[0] == 'common-room-hourly-scheduling' :
            return json.dumps(self.catalogList['common-room-hourly-scheduling'])
        
        elif uri[0] == 'patient-room-hourly-scheduling' :
            return json.dumps(self.catalogList['patient-room-hourly-scheduling'])

        elif uri[0] == 'patient-temperature-base-topic' :
            return json.dumps(self.catalogList['patient-temperature-base-topic'])

        elif uri[0] == 'patient-saturation-base-topic' :
            return json.dumps(self.catalogList['patient-saturation-base-topic'])

        elif uri[0] == 'patient-room-temperature-base-topic' :
            return json.dumps(self.catalogList['patient-room-temperature-base-topic'])
        
        elif uri[0] == 'patient-room-light-base-topic' :
            return json.dumps(self.catalogList['patient-room-light-base-topic'])
        

        elif uri[0] == 'common-room-base-topic' :
            return json.dumps(self.catalogList['common-room-base-topic'])

        elif uri[0] == 'alarm-base-topic' :
            return json.dumps(self.catalogList['alarm-base-topic'])
        elif uri[0] == 'patient-room-light-command-base-topic' :
            return json.dumps(self.catalogList['patient-room-light-command-base-topic'])
        elif uri[0] == 'patient-room-temperature-command-base-topic' :
            return json.dumps(self.catalogList['patient-room-temperature-command-base-topic'])
        elif uri[0] == 'common-room-command-base-topic' :
            return json.dumps(self.catalogList['common-room-command-base-topic'])

        elif uri[0] == 'devices' :
            return json.dumps(self.catalogList["devices"])

        elif uri[0] == 'device' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'deviceID missing')
            for device in self.catalogList['devices'] :
                if device['deviceID'] == str(uri[1]) :
                    return json.dumps(device)
            raise cherrypy.HTTPError(400,'device not found')
        
        elif uri[0] == 'services' :
            return json.dumps(self.catalogList["services"])
        elif uri[0] == 'service' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'serviceID missing')
            for service in self.catalogList['services'] :
                if service['serviceID'] == int(uri[1]) :
                    return json.dumps(device)
            raise cherrypy.HTTPError(400,'service not found')

        elif uri[0] == 'patients' :
            patients = []
            for room in self.catalogList['room-list']:
                patients += room['patients']
            return json.dumps(patients)

        elif uri[0] == 'patient' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'patientID missing')
            for room in self.catalogList['room-list']:
                patients = room['patients']
                for patient in patients :
                    if patient['patientID'] == int(uri[1]) :
                        return json.dumps(patient)
            raise cherrypy.HTTPError(400,'patient not found')

        elif uri[0] == 'common-room':
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'roomID missing')
            for room in self.catalogList['common-room-list'] :
                if room['roomID'] == int(uri[1]) :
                    return json.dumps(room)
            raise cherrypy.HTTPError(400,'room not found')

        elif uri[0] == 'room':
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'roomID missing')
            for room in self.catalogList['room-list'] :
                if room['roomID'] == int(uri[1]) :
                    return json.dumps(room)
            raise cherrypy.HTTPError(400,'room not found')

        elif uri[0] == 'telegram-user':
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'roomID missing')
            for user in self.catalogList['telegram-user-id-list'] :
                if user['user-id'] == int(uri[1]) :
                    return json.dumps(user)
            raise cherrypy.HTTPError(400,'room not found')

        else : 
            raise cherrypy.HTTPError(404,'operation not found')


    def POST(self,*uri):
        if len(uri) != 1 :
            raise cherrypy.HTTPError(400,'Wrong parameters number')

        if uri[0] == 'add-device' :
            
            newDevice = json.loads(cherrypy.request.body.read())
            for device in self.catalogList['devices'] :
                if device['deviceID'] == newDevice['deviceID'] :
                    raise cherrypy.HTTPError(400,"device already exists")
            newDevice['timestamp'] = str(datetime.datetime.today())
            self.catalogList['devices'].append(newDevice)
            return

        elif uri[0] == 'add-common-room' :
            
            newRoom = json.loads(cherrypy.request.body.read())
            for room in self.catalogList['common-room-list'] :
                if room['roomID'] == newRoom['roomID'] :
                    raise cherrypy.HTTPError(400,"room already exists")
            self.catalogList['common-room-list'].append(newRoom)
            return

        elif uri[0] == 'add-room' :
            
            newRoom = json.loads(cherrypy.request.body.read())
            for room in self.catalogList['room-list'] :
                if room['roomID'] == newRoom['roomID'] :
                    raise cherrypy.HTTPError(400,"room already exists")
            self.catalogList['room-list'].append(newRoom)
            return

        elif uri[0] == 'add-patient' :

            newPatient = json.loads(cherrypy.request.body.read())
            patients = []
            found_room = False
            for room in self.catalogList['room-list']:
                patients += room['patients']
                if room['roomID'] == newPatient['roomID']:
                    found_room = True
            if not found_room:
                raise cherrypy.HTTPError(406, "room does not exist")
            for patient in patients:
                if patient['patientID'] == newPatient['patientID'] :
                    raise cherrypy.HTTPError(400,"patient already exists")
            for room in self.catalogList['room-list']:
                if newPatient['roomID'] == room['roomID']:
                    room['patients'].append(newPatient)
                    return
            return 

        elif uri[0] == 'add-telegram-user' :
            newUser = json.loads(cherrypy.request.body.read())
            for user in self.catalogList['telegram-user-id-list'] :
                if user['user-id'] == newUser['user-id'] :
                    raise cherrypy.HTTPError(400,"id already exists")
            self.catalogList['telegram-user-id-list'].append(newUser)
            return 

        elif uri[0] == 'add-service' :
            newService = json.loads(cherrypy.request.body.read())
            for service in self.catalogList['services'] :
                if service['serviceID'] == newService['serviceID'] :
                    raise cherrypy.HTTPError(400,"service already exists")
            newService['timestamp'] = str(datetime.datetime.today())
            self.catalogList['services'].append(newService)
            return 

        else : 
            raise cherrypy.HTTPError(404,'operation not found')

    def PUT(self,*uri):

        if len(uri) != 1 :
            raise cherrypy.HTTPError(400,'Wrong parameters number')
        
        if uri[0] == 'update-device' :
            newDevice = json.loads(cherrypy.request.body.read())
            newDevice['timestamp'] = str(datetime.datetime.today())
            id = newDevice['deviceID']
            found = False
            for i in range(len(self.catalogList['devices'])) :
                if self.catalogList['devices'][i]['deviceID'] == id :
                    self.catalogList['devices'][i]['timestamp'] = str(datetime.datetime.today())
                    found = True
            if not found:
                self.catalogList['devices'].append(newDevice)
            return

        elif uri[0] == 'update-patient' :
            newPatient = json.loads(cherrypy.request.body.read())
            id = newPatient['patientID']
            # Check that the room exists
            found_room = False
            for room in self.catalogList['room-list']:
                if room['roomID'] == newPatient['roomID']:
                    found_room = True
            if not found_room:
                raise cherrypy.HTTPError(406,'room does not exist')
            found_patient = False
            for room in self.catalogList['room-list']:
                for patient in room['patients']:
                    if patient['patientID'] == newPatient['patientID']:
                        found_patient = True
            if not found_patient:
                raise cherrypy.HTTPError(400,'patient not found')
            
            for room in self.catalogList['room-list']:
                # Delete the old patient
                room['patients'][:] = [patient for patient in room['patients'] if patient['patientID'] != newPatient['patientID']]
                # Insert the new patient
                if room['roomID'] == newPatient['roomID']:
                    room['patients'].append(newPatient)
            return
                    
        elif uri[0] == 'update-room' :
            
            newRoom = json.loads(cherrypy.request.body.read())
            rooms = self.catalogList['room-list']
            if 'roomID_old' in newRoom:
                oldRoomID = newRoom['roomID_old']
                del newRoom['roomID_old']
                for room in rooms:
                    if room['roomID'] == newRoom['roomID']:
                        raise cherrypy.HTTPError(400, 'room already existing')
                for room in rooms:
                    if room['roomID'] == oldRoomID:
                        room['roomID'] = newRoom['roomID']

            self.catalogList['room-list'] = [newRoom if int(room['roomID']) == int(newRoom['roomID']) else room for room in rooms]
            return

        elif uri[0] == 'update-common-room' :
            
            newRoom = json.loads(cherrypy.request.body.read())
            rooms = self.catalogList['common-room-list']
            if 'roomID_old' in newRoom:
                oldRoomID = newRoom['roomID_old']
                del newRoom['roomID_old']
                for room in rooms:
                    if room['roomID'] == newRoom['roomID']:
                        raise cherrypy.HTTPError(400, 'room already existing')
                for room in rooms:
                    if room['roomID'] == oldRoomID:
                        room['roomID'] = newRoom['roomID']

            self.catalogList['common-room-list'] = [newRoom if int(room['roomID']) == int(newRoom['roomID']) else room for room in rooms]
            return
            

        elif uri[0] == 'update-service' :
            newService = json.loads(cherrypy.request.body.read())
            newService['timestamp'] = str(datetime.datetime.today())
            id = newService['serviceID']
            found = False
            for i in range(len(self.catalogList['services'])) :
                if self.catalogList['services'][i]['serviceID'] == id :
                    self.catalogList['services'][i]['timestamp'] = str(datetime.datetime.today())
                    found = True
            if not found:
                self.catalogList['services'].append(newService)
            return 

        elif uri[0] == 'update-telegram-user':
            newUser = json.loads(cherrypy.request.body.read())
            if newUser['user-id'] not in list(map(lambda user: user['user-id'], self.catalogList['telegram-user-id-list'])) :
                 raise cherrypy.HTTPError(400, 'user not found')
            self.catalogList['telegram-user-id-list'][:] = \
                [newUser if newUser['user-id'] == user['user-id'] else user for user in self.catalogList['telegram-user-id-list']]
            return
        
        else : 
            raise cherrypy.HTTPError(404,'operation not found')

    
    def DELETE(self,*uri) :
        if len(uri) != 2 :
            raise cherrypy.HTTPError(400,'Wrong parameters number')

        if uri[0] == 'delete-patient' :
            patientID = int(uri[1])
            found = False
            rooms = self.catalogList['room-list']
            for room in rooms:
                prev_len = len(room['patients'])
                room['patients'][:] = [patient for patient in room['patients'] if patient['patientID'] != patientID]
                new_len = len(room['patients'])
                if new_len < prev_len:
                    found = True
            if not found:
                raise cherrypy.HTTPError(400,'patient not found')
        
        elif uri[0] == 'delete-room' :
            roomID = int(uri[1])
            found = False
            prev_len = len(self.catalogList['room-list'])
            self.catalogList['room-list'][:] = [room for room in self.catalogList['room-list'] if room['roomID'] != roomID]
            new_len = len(self.catalogList['room-list'])
            if new_len < prev_len:
                found = True
            if not found:
                raise cherrypy.HTTPError(400,'room not found')

        elif uri[0] == 'delete-common-room' :
            roomID = int(uri[1])
            found = False
            prev_len = len(self.catalogList['common-room-list'])
            self.catalogList['common-room-list'][:] = [room for room in self.catalogList['common-room-list'] if room['roomID'] != roomID]
            new_len = len(self.catalogList['common-room-list'])
            if new_len < prev_len:
                found = True
            if not found:
                raise cherrypy.HTTPError(400,'room not found')
        
        elif uri[0] == 'delete-service' :
            serviceID = int(uri[1])
            found = False
            prev_len = len(self.catalogList['services'])
            self.catalogList['services'][:] = [service for service in self.catalogList['services'] if service['serviceID'] != serviceID]
            new_len = len(self.catalogList['services'])
            if new_len < prev_len:
                found = True
            if not found:
                raise cherrypy.HTTPError(400,'service not found')

        elif uri[0] == 'delete-telegram-user' :
            userID = int(uri[1])
            found = False
            prev_len = len(self.catalogList['telegram-user-id-list'])
            self.catalogList['telegram-user-id-list'][:] = [user for user in self.catalogList['telegram-user-id-list'] if user['user-id'] != userID]
            new_len = len(self.catalogList['telegram-user-id-list'])
            if new_len < prev_len:
                found = True
            if not found:
                raise cherrypy.HTTPError(400,'user not found')
        
        else :
            raise cherrypy.HTTPError(404,'operation not found')



if __name__ == "__main__" :
    conf={ 
        '/':{
            'request.dispatch':cherrypy.dispatch.MethodDispatcher(),
            'tool.session.on':True
        }
    }
    cherrypy.config.update({'server.socket_host': '0.0.0.0'})
    c = Catalog()
    cherrypy.tree.mount(c,'/catalog',conf)
    cherrypy.engine.start()
    c.refreshList()
    cherrypy.engine.block()
    

