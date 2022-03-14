import time

class RaspberryEmulator :
    def __init__(self) :
        self.rooms = {}
        r = requests.get("https://localhost:8080/catalog/common-room-list")
        c = r.json()
        self.commonRoomList = c['common-room-list']


        for room in self.commonRoomList :
             r = requests.post("https://localhost:8080/catalog/add-device",data = {
                                                                    'deviceID' : room,
                                                                    'name' : 'light-patient-room-monitor'
        })


    def emulateCommonRoomData(self) :
        while True :
            time.sleep(60*60) #send data every hour
            for room in self.commonRoomList :
                #emulateCommonRoomData(room)
                pass


    def emulatePatientRoomData(self) :
        while True :
            time.sleep(60*60) #send data every hour
            for room in list(self.rooms.keys()) :
                if self.rooms[room].length != 0 :
                    #emulateRoomData(room)
                    pass

    def emulatePatientData(self) :
        while True :
            time.sleep(60*1) #send data every minute
            for room in list(self.rooms.keys()) :
                for id in self.rooms[room] :
                    #emulatePatientData(id)                        
                    pass
            
    def updateServices(self) :
        while True :
            time.sleep(100) #update every 100 seconds
            for commonRoom in self.commonRoomList :
                r = requests.put("https://localhost:8080/catalog/update-device",data = {
                            'deviceID' : commonRoom,
                            'name' : 'patient-room-device-'+id
                        })



            for room in list(self.rooms.keys()) :
                if self.rooms[room].length != 0:
                    r = requests.put("https://localhost:8080/catalog/update-device",data = {
                            'deviceID' : id,
                            'name' : 'patient-room-device-'+id
                        })
                    for id in self.rooms[room] :
                        r = requests.put("https://localhost:8080/catalog/update-device",data = {
                            'deviceID' : id,
                            'name' : 'patient-device-'+id
                        })
            

    def listenUserCommand(self) :
        choice = int(input("Inserisci 1 per aggiungere paziente, 0 per rimuovere paziente, 2 per terminare "))
        #lanciare thread che registra i device relativi a stanze e pazienti
    
        while choice != 2 :
            room = 0
            patientId = 0
            if choice == 1 :
                patientId = int(input("Inserisci id paziente da aggiungere "))
                roomId = int(input("Inserisci numero stanza "))

                if roomId in self.rooms :
                    if patientId not in self.rooms[roomId] :
                        self.rooms[roomId].append(patientId)
                        r = requests.post("https://localhost:8080/catalog/add-device",data = {
                                                                            'deviceID' : patientId,
                                                                            'name' : 'light-patient-room-monitor'
        })
                else :
                    self.rooms[roomId] = [patientId]
                    r = requests.post("https://localhost:8080/catalog/add-device",data = {
                                                                        'deviceID' : roomId,
                                                                        'name' : 'light-patient-room-monitor'
                                                                    })
                    r = requests.post("https://localhost:8080/catalog/add-device",data = {
                                                                    'deviceID' : patientId,
                                                                    'name' : 'light-patient-room-monitor'
        })
            if choice == 0 :
                patientId = int(input("Inserisci id paziente da rimuvere "))
                for room in list(self.rooms.keys()) :
                    for id in self.rooms[room] :
                        if id == patientId :
                            self.rooms[room].remove(id)
            print(self.rooms)
            choice = int(input("Inserisci 1 per aggiungere paziente, 0 per rimuovere paziente, 2 per terminare "))




if __name__ == "__main__" :  
    e = RaspberryEmulator()
    e.listenUserCommand()
