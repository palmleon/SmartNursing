from calendar import c
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
                # expect on if runned at 21h
                self.mqttClient.myPublish("group01/IoTProject/PatientRoom/1",{"bn" : "test","bt":0,"e" : [{"n":"presence","u":"bool","v":0},{"n":"temperature","u":"cel","v":27}]})
            elif choice == 0:
                return
            elif choice == 2:
                # expected off if runned at 21h
                self.mqttClient.myPublish("group01/IoTProject/CommonRoom/3",{"bn" : "test","bt":0,"e" : [{"n":"presence","u":"bool","v":0},{"n":"temperature","u":"cel","v":24}]})
            elif choice == 3:
                # expected 100 if runned at 22
                self.mqttClient.myPublish("group01/IoTProject/PatientRoom/1",{"bn" : "test","bt":0,"e" : {"n":"light","u":"bool","v":1}})
            elif choice == 4:
                # low battery
                self.mqttClient.myPublish("group01/IoTProject/Patient/Temperature/1",{"bn" : "testTemperature","bt":0,"e" : [{"n":"battery","u":"V","v":2}, {"n":"temperature","u":"cel","v":37}]})
            elif choice == 5:
                # fever
                self.mqttClient.myPublish("group01/IoTProject/Patient/Temperature/1",{"bn" : "testTemperature","bt":0,"e" : [{"n":"battery","u":"V","v":3}, {"n":"temperature","u":"cel","v":39}]})
            elif choice == 6:
                # fibbrillation
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[97,97,97,97,97,97,97,97,97,97]}, {"n":"pulse rate","u":"bpm","v":[70,80,90,70,80,80,90,70,70,90]}]})
            elif choice == 7:
                # bad positioned or removed
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[0,0,1,0,0,1,0,0,1,0]},{"n":"saturation","u":"perc","v":[0,0,0,0,0,0,0,0,0,0]}, {"n":"pulse rate","u":"bpm","v":[0,0,0,0,0,0,0,0,0,0]}]})
            elif choice == 8:
                # battito cardiaco basso
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[97,97,97,97,97,97,97,97,97,97]}, {"n":"pulse rate","u":"bpm","v":[50,50,50,50,50,50,50,50,50,50]}]})
            elif choice == 9:
                #  ipossia
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[90,91,91,90,91,90,91,91,91,90]}, {"n":"pulse rate","u":"bpm","v":[80,80,80,80,80,80,80,80,80,80]}]})

            
            
            choice = int(input('1 to emulate a date in the patient room for the temperature managment\n2 to emulate a data in the common room for temeperature\n3 to emulate a data in the patient room for the luminosity\n0 to exit'))




if __name__ == "__main__" :
    test = TestScript()
    test.startScript()
