import json
import cherrypy
import time
import datetime

#Accesso al contenuto di self.catalog in parallelo? sia da metodo refresh che metodi REST

class Catalog(object) :
    exposed = True
    def __init__(self) :
        self.fp = open("catalog.json","r")
        self.catalogList = json.load(self.fp)
        self.fp.close()
        

    def computeDifference(self,t2,t1) :
        t1 = datetime.datetime.strptime(t1, "%Y-%m-%d %H:%M:%S.%f")
        diff = t2-t1
        diff = diff.total_seconds()
        return diff/60

    def refreshList(self) :
        while True :
            time.sleep(60*20) # Tempo di attesa prima di partire a refreshare
            #print('parto a refreshare')
            #Elimino device e servizi che non sono aggiornati da più di 2 minuti
            self.catalogList['devices'] = list(filter(lambda dev : self.computeDifference(datetime.datetime.today(),dev['timestamp']) < 2,self.catalogList['devices']))
            self.catalogList['services'] = list(filter(lambda dev : self.computeDifference(datetime.datetime.today(),dev['timestamp']) < 2,self.catalogList['services']))
            self.fp = open("catalog.json","w")
            json.dump(self.catalogList,self.fp)
            self.fp.close()
            

    def GET(self,*uri,**path):
        if len(uri) != 1 :
            raise cherrypy.HTTPError(400,'Wrong parameters number')

        if uri[0] == 'message-broker' :
            return json.dumps(self.catalogList["message-broker"])

        elif uri[0] == 'city' :
            return json.dumps(self.catalogList['city'])
        elif uri[0] == 'api-weather' :
            return json.dumps(self.catalogList['api-weather'])
        elif uri[0] == 'desired-temperature' :
            return json.dumps(self.catalogList['desired-temperature'])
        
        elif uri[0] == 'telegram-chat-id-list' :
            return json.dumps(self.catalogList['telegram-chat-id-list'])
        
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

        elif uri[0] == 'patient-room-base-topic' :
            return json.dumps(self.catalogList['patient-room-base-topic'])
        
        elif uri[0] == 'common-room-base-topic' :
            return json.dumps(self.catalogList['common-room-base-topic'])

        elif uri[0] == 'alarm-base-topic' :
            return json.dumps(self.catalogList['alarm-base-topic'])
        elif uri[0] == 'patient-room-command-base-topic' :
            return json.dumps(self.catalogList['patient-room-command-base-topic'])
        elif uri[0] == 'common-room-command-base-topic' :
            return json.dumps(self.catalogList['common-room-command-base-topic'])

        elif uri[0] == 'devices' :
            return json.dumps(self.catalogList["devices"])

        elif uri[0] == 'device' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'deviceID missing')
            for device in self.catalogList['devices'] :
                if device['deviceID'] == int(uri[1]) :
                    return json.dumps(device)
            raise cherrypy.HTTPError(404,'device not found')
        
        elif uri[0] == 'services' :
            return json.dumps(self.catalogList["services"])
        elif uri[0] == 'service' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'serviceID missing')
            for service in self.catalogList['services'] :
                if service['serviceID'] == int(uri[1]) :
                    return json.dumps(device)
            raise cherrypy.HTTPError(404,'service not found')

        elif uri[0] == 'patients' :
            return json.dumps(self.catalogList["patients"])

        elif uri[0] == 'patient' :
            if len(uri) != 2 :
                raise cherrypy.HTTPError(400,'patientID missing')
            for patient in self.catalogList['patients'] :
                if device['patientID'] == int(uri[1]) :
                    return json.dumps(patient)
            raise cherrypy.HTTPError(404,'patient not found')
        else : 
            raise cherrypy.HTTPError(400,'operation not found')

    def POST(self,*uri,**path):
        if len(uri) != 1 :
            raise cherrypy.HTTPError(500,'Wrong parameters number')

        if uri[0] == 'add-device' :
            
            newDevice = json.loads(cherrypy.request.body.read())
            for device in self.catalogList['devices'] :
                if device['deviceID'] == newDevice['deviceID'] :
                    raise cherrypy.HTTPError(400,"device already exists")
            newDevice['timestamp'] = str(datetime.datetime.today())
            self.catalogList['devices'].append(newDevice)
            return

        elif uri[0] == 'add-patient' :
            newPatient = json.loads(cherrypy.request.body.read())
            for patient in self.catalogList['patients'] :
                if patient['patientID'] == newPatient['patientID'] :
                    raise cherrypy.HTTPError(400,"patient already exists")
            self.catalogList['patients'].append(newPatient)
            return 

        elif uri[0] == 'add-telegram-chat-id' :
            newId = json.loads(cherrypy.request.body.read())
            for id in self.catalogList['telegram-chat-id-list'] :
                if id == newId :
                    raise cherrypy.HTTPError(400,"id already exists")
            self.catalogList['telegram-chat-id-list'].append(newId)
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
            raise cherrypy.HTTPError(400,'operation not found')

        

    def PUT(self,*uri,**path):
        if len(uri) != 1 :
            raise cherrypy.HTTPError(400,'Wrong parameters number')

        if uri[0] == 'update-device' :
            newDevice = json.loads(cherrypy.request.body.read())
            #print(newDevice)
            id = newDevice['deviceID']
            for i in range(len(self.catalogList['devices'])) :
                if self.catalogList['devices'][i]['deviceID'] == id :
                    self.catalogList['devices'][i]['timestamp'] = str(datetime.datetime.today())
            return 
        if uri[0] == 'update-service' :
            newService = json.loads(cherrypy.request.body.read())
            newService['timestamp'] = str(datetime.datetime.today())
            id = newService['serviceID']
            for i in range(len(self.catalogList['services'])) :
                if self.catalogList['services'][i]['serviceID'] == id :
                    self.catalogList['services'][i]['timestamp'] = str(datetime.datetime.today())
            return 
        
        else : 
            raise cherrypy.HTTPError(400,'operation not found')

    
    def DELETE(self,*uri,**path) :
        if len(uri) != 1 :
            raise cherrypy.HTTPError(500,'Wrong parameters number')

        if uri[0] == 'delete-patient' :
            id = int(uri[1])
            for i in range(len(self.catalogList['patients'])) :
                if self.catalogList['patients'][i]['patientID'] == id :
                    del self.catalogList['patients'][i]
            raise cherrypy.HTTPError(404,'patient not found')
        
        #Is necessary?
        elif uri[0] == 'delete-service' :
            id = int(uri[1])
            for i in range(len(self.catalogList['services'])) :
                if self.catalogList['services'][i]['serviceID'] == id :
                    del self.catalogList['services'][i]
            raise cherrypy.HTTPError(404,'service not found')

        elif uri[0] == 'delete-telegram-chat-id' :
            id = int(uri[1])
            for i in range(len(self.catalogList['telegram-chat-id-list'])) :
                if self.catalogList['telegram-chat-id-list'][i] == id :
                    del self.catalogList['telegram-chat-id-list'][i]
            raise cherrypy.HTTPError(404,'id  not found')
        
       
        else :
            raise cherrypy.HTTPError(400,'operation not found')




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
    

