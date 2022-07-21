from MyMQTT import *


class TestScript():
    def __init__(self) :
        self.mqttClient = MyMQTT('scriptToTestTheSmartNursing',"mqtt.eclipseprojects.io",1883,self)
        self.patientId = 1
        self.roomId = 1
        self.mqttClient.start()

    def startScript(self):
        choice = int(input('1 to emulate a temperature 27 °C in the patient room, when the patient is not present \n2 to emulate a temperature of 24 °C in a common room during an unexpected presence, when there are no patients\n3 to send a data to the light monitor, indicating that the light is on\n4 to send a message to the patient monitor where the sensor battery is low\n5 to emulate a patient with a body temperature of 39 °C\n6 to emulate a patient in a fibbrillation state\n7 to emulate a bad positioned sensor\n8 to emulate a low pulse rate\n9 to emulate am hypoxia'))
        while choice != 0:
            if choice == 1 :
                # expect on if runned at 21h
                self.mqttClient.myPublish("group01/IoTProject/PatientRoom/Temperature/1",{"bn" : "test","bt":0,"e" : [{"n":"presence","u":"bool","v":0},{"n":"temperature","u":"cel","v":27}]})
                print({"bn" : "test","bt":0,"e" : [{"n":"presence","u":"bool","v":0},{"n":"temperature","u":"cel","v":27}]})
            elif choice == 0:
                return
            elif choice == 2:
                # expected off if runned at 21h
                self.mqttClient.myPublish("group01/IoTProject/CommonRoom/3",{"bn" : "test","bt":0,"e" : [{"n":"presence","u":"bool","v":0},{"n":"temperature","u":"cel","v":24}]})
                print({"bn" : "test","bt":0,"e" : [{"n":"presence","u":"bool","v":0},{"n":"temperature","u":"cel","v":24}]})
            elif choice == 3:
                # expected 100 if runned at 22
                self.mqttClient.myPublish("group01/IoTProject/PatientRoom/Light/1",{"bn" : "test","bt":0,"e" : {"n":"light","u":"bool","v":1}})
                print({"bn" : "test","bt":0,"e" : {"n":"light","u":"bool","v":1}})
            elif choice == 4:
                # low battery
                self.mqttClient.myPublish("group01/IoTProject/Patient/Temperature/1",{"bn" : "testTemperature","bt":0,"e" : [{"n":"battery","u":"V","v":2}, {"n":"temperature","u":"cel","v":37}]})
                print({"bn" : "testTemperature","bt":0,"e" : [{"n":"battery","u":"V","v":2}, {"n":"temperature","u":"cel","v":37}]})
            elif choice == 5:
                # fever
                self.mqttClient.myPublish("group01/IoTProject/Patient/Temperature/1",{"bn" : "testTemperature","bt":0,"e" : [{"n":"battery","u":"V","v":3}, {"n":"temperature","u":"cel","v":39}]})
                print({"bn" : "testTemperature","bt":0,"e" : [{"n":"battery","u":"V","v":3}, {"n":"temperature","u":"cel","v":39}]})
            elif choice == 6:
                # fibbrillation
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[97,97,97,97,97,97,97,97,97,97]}, {"n":"pulse rate","u":"bpm","v":[70,80,90,70,80,80,90,70,70,90]}]})
                print({"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[97,97,97,97,97,97,97,97,97,97]}, {"n":"pulse rate","u":"bpm","v":[70,80,90,70,80,80,90,70,70,90]}]})
            elif choice == 7:
                # bad positioned or removed
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[0,0,1,0,0,1,0,0,1,0]},{"n":"saturation","u":"perc","v":[0,0,0,0,0,0,0,0,0,0]}, {"n":"pulse rate","u":"bpm","v":[0,0,0,0,0,0,0,0,0,0]}]})
                print({"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[0,0,1,0,0,1,0,0,1,0]},{"n":"saturation","u":"perc","v":[0,0,0,0,0,0,0,0,0,0]}, {"n":"pulse rate","u":"bpm","v":[0,0,0,0,0,0,0,0,0,0]}]})
            elif choice == 8:
                # battito cardiaco basso
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[97,97,97,97,97,97,97,97,97,97]}, {"n":"pulse rate","u":"bpm","v":[50,50,50,50,50,50,50,50,50,50]}]})
                print({"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[97,97,97,97,97,97,97,97,97,97]}, {"n":"pulse rate","u":"bpm","v":[50,50,50,50,50,50,50,50,50,50]}]})
            elif choice == 9:
                #  ipossia
                self.mqttClient.myPublish("group01/IoTProject/Patient/Pulsation/1",{"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[90,91,91,90,91,90,91,91,91,90]}, {"n":"pulse rate","u":"bpm","v":[80,80,80,80,80,80,80,80,80,80]}]})
                print({"bn" :"testOximeter","bt":0,"e":[{"n":"battery","u":"V","v":3},{"n":"perfusion index","u":"perc","v":[5,5,5,5,5,5,5,5,5,5]},{"n":"saturation","u":"perc","v":[90,91,91,90,91,90,91,91,91,90]}, {"n":"pulse rate","u":"bpm","v":[80,80,80,80,80,80,80,80,80,80]}]})
            
            
            choice = int(input('\n\n1 to emulate a temperature 27 °C in the patient room, when the patient is not present \n2 to emulate a temperature of 24 °C in a common room during an unexpected presence, when there are no patients\n3 to send a data to the light monitor, indicating that the light is on\n4 to send a message to the patient monitor where the sensor battery is low\n5 to emulate a patient with a body temperature of 39 °C\n6 to emulate a patient in a fibbrillation state\n7 to emulate a bad positioned sensor\n8 to emulate a low pulse rate\n9 to emulate am hypoxia'))




if __name__ == "__main__" :
    test = TestScript()
    test.startScript()
