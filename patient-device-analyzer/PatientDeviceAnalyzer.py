from MyMQTT import MyMQTT
import time
import json
import requests
import threading

class PatientDeviceAnalyzer():
  def __init__(self):
    # Reading configuration file
    fp=open('PatientDeviceAnalyzer_config.json')
    conf_file = json.load(fp)
    fp.close()
    # Getting service Id, service name and registry host
    self.__clientID=conf_file["serviceID"]
    self.__name=conf_file["name"]
    self.__register=conf_file["host"]
    # Getting service update time
    self.__update_service_time_seconds=conf_file["update_service_time_seconds"]
    # Getting service waiting time
    self.__control_time_seconds=conf_file["control_time_seconds"]
    # Getting sensor names
    self.__T_sensor_name=conf_file["sensor_names"]["thermometer"]
    self.__P_sensor_name=conf_file["sensor_names"]["pulse_oximeter"]
    # Getting alarm template and messages
    self.__alert=conf_file["template_alarm"]
    messagesdict=conf_file["alarm_messages"]
    self.__alarm_T=messagesdict["alarm_T"].split("{}")
    self.__alarm_P=messagesdict["alarm_P"].split("{}")
    # Registration
    r=requests.post(self.__register+"/add-service",data= json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
    
    # Request for broker information
    r = requests.get(self.__register+"/message-broker")
    mb = r.json()
    self.__broker=mb['name']
    self.__port=mb['port']
    # Request for publish base topic
    r = requests.get(self.__register+"/alarm-base-topic")
    self.__base_topic_pub = r.json()

    # Creating client
    self.client = MyMQTT(self.__name, self.__broker, self.__port, None)
    # Starting client
    self.client.start()
    time.sleep(2)

    # Request for hourly scheduling (night time)
    r = requests.get(self.__register+"/patient-room-hourly-scheduling")
    d=r.json()
    self.__hours=d["night"] #d[0]=Starting hour d[1]=Stop hour
  
  def control(self):
    while True:
      time.sleep(self.__control_time_seconds)
      #It's Night?
      ###TODO###: REMOVE COMMENT AFTER DEBUG
      #if time.localtime()[3]>=self.__hours[0] or time.localtime()[3]<=self.__hours[1]:
      if True:
        # Request for patient list
        r = requests.get(self.__register+"/patients")
        patient_dict=r.json()
        #print(patient_dict)
        patient_IDs=[]
        for patient in patient_dict:
          patient_IDs.append(patient["patientID"])
        # Request for device list
        r = requests.get(self.__register+"/devices")
        all_devices=r.json()
        #print(all_devices)
        for patient in patient_IDs: #Checking one patient each time
          sensors=[]
          alarm=[]
          for device in all_devices:
            if "patientID" in device: # Checking if it's a room or patient device
              if str(patient)==str(device["patientID"]):
                sensors.append(device["name"]) # Sensor found

          if self.__T_sensor_name not in sensors: # Checking if thermometer was found
            alarm.append(self.__alarm_T[0]+str(patient)+self.__alarm_T[1])

          if self.__P_sensor_name not in sensors: # Checking if pulse oximeter was found
            alarm.append(self.__alarm_P[0]+str(patient)+self.__alarm_P[1])
          #print(alarm)
          for alert in alarm:
            # Publish a message for each sensor not found
            to_pub=self.__alert
            to_pub["alert"]=alert
            to_pub["time"]=time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
            self.client.myPublish(self.__base_topic_pub+str(patient),to_pub)
  
  def updateService(self) :
    while True :
      time.sleep(self.__update_service_time_seconds)
      r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))

if __name__ == "__main__" :
  A=PatientDeviceAnalyzer()
  t1 = threading.Thread(target=A.control)
  t2 = threading.Thread(target=A.updateService)
  t1.start()
  t2.start()
  t1.join()
  t2.join()
