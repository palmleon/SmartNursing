from MyMQTT import *


class TestScript():
    def __init__(self) :
        self.mqttClient = MyMQTT('scriptToTestTheSmartClinic',"mqtt.eclipseprojects.io",1883,self)
        self.patientId = 1
        self.roomId = 1
        self.mqttClient.start()

    def startScript(self):
        choice = int(input('1 to emulate a..\n2 to emulate a ..\n0 to exit'))
        while choice != 0:
            if choice == 1 :
                # expect on if runned at 21
                self.mqttClient.myPublish("group01/IoTProject/PatientRoom/1",{"bn" : "test","bt":0,"e" : [{"n":"light","u":"bool","v":0},{"n":"presence","u":"bool","v":0}, {"n":"temperature","u":"cel","v":27}]})
            elif choice == 0:
                return
            elif choice == 2:
                # expected off if runned at 21
                self.mqttClient.myPublish("group01/IoTProject/CommonRoom/3",{"bn" : "test","bt":0,"e" : [{"n":"light","u":"bool","v":0},{"n":"presence","u":"bool","v":0}, {"n":"temperature","u":"cel","v":24}]})
            elif choice == 3:
                # expected 100 if runned at 22
                self.mqttClient.myPublish("group01/IoTProject/PatientRoom/1",{"bn" : "test","bt":0,"e" : [{"n":"light","u":"bool","v":1},{"n":"presence","u":"bool","v":0}, {"n":"temperature","u":"cel","v":24}]})
            choice = int(input('1 to emulate a date in the patient room for the temperature managment\n2 to emulate a data in the common room for temeperature\n3 to emulate a data in the patient room for the luminosity\n0 to exit'))




if __name__ == "__main__" :
    test = TestScript()
    test.startScript()
