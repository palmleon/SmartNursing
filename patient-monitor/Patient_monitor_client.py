from Patient_monitor_Analyzer import *
from MyMQTT import MyMQTT
import time
from datetime import datetime
import json
import requests

class Patient_Monitor_client():
  def __init__(self):
    # Reading configuration file
    fp=open('Patient_monitor_config.json')
    conf_file = json.load(fp)
    fp.close()
    # Getting service Id, service name and registry host
    self.__clientID=conf_file["serviceID"]
    self.__name=conf_file["name"]
    self.__register=conf_file["host"]
    # Getting service update time
    self.__update_service_time_seconds = conf_file['update_service_time_seconds']
    # Getting alarm template and messages
    self.__alert=conf_file["template_alarm"]
    messagesDict=conf_file["alarm_messages"]
    # Getting Thresholds
    ThresholdsDict=conf_file["Thresholds"]
    # Registration
    try :
      r = requests.post(self.__register+"/add-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
      
      # Request for broker information
      r = requests.get(self.__register+"/message-broker")
      mb = r.json()
      self.__broker=mb['name']
      self.__port=mb['port']
      # Request for subscibe and publish base topics
      r = requests.get(self.__register+"/patient-saturation-base-topic")
      mb = r.json()
      self.__topic_sub_P=mb+"+"

      r = requests.get(self.__register+"/patient-temperature-base-topic")
      mb = r.json()
      self.__topic_sub_T=mb+"+"

      r = requests.get(self.__register+"/alarm-base-topic")
      mb = r.json()
      self.__base_topic_pub=mb
    except :
      print("ERROR: init failed, restart container")
      exit(-1)

    # Creating analyzer
    self.analyzer=Patient_Monitor(messagesDict,ThresholdsDict)

    # Creating client
    self.client = MyMQTT(self.__name, self.__broker, self.__port, self)

    # Starting client
    self.client.start()
    time.sleep(2)

    # Subscribing
    self.client.mySubscribe(self.__topic_sub_T)
    self.client.mySubscribe(self.__topic_sub_P)
  
  def updateService(self) :
    while True :
      time.sleep(self.__update_service_time_seconds)
      try :

        r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
        if r.ok == False :
          print("ERROR: update failed")
      except :
        print("ERROR: update failed")
      #print(r)


  def notify(self,topic,msg):
    print(f"\nIncoming message from topic: {topic}\n")
    # Getting message in json format
    msg=json.loads(msg)
    # Getting patient ID from topic
    ID_P=topic.split("/")[-1]
    # Getting events list
    evento=msg["e"]
    
    
    battery=0
    Pi=[]
    pulse=[]
    sat=[]
    temp=-1
    for ev in evento:
      if ev["n"]=="battery":
        battery=ev["v"]

      if ev["n"]=="perfusion index":
        Pi=ev["v"]
      
      if ev["n"]=="saturation":
        sat=ev["v"]
      
      if ev["n"]=="pulse rate":
        pulse=ev["v"]
      
      if ev["n"]=="temperature":
        temp=ev["v"]
    
    if temp>-1:
      r=self.analyzer.Temperature(ID_P,temp,battery)
      if r!=None:
        to_pub=self.__alert
        to_pub["alert"]=r
        to_pub["time"]=time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
        # Publish alert
        self.client.myPublish(self.__base_topic_pub+ID_P,to_pub)
    
    if len(Pi)>1:
      #print(f"Ottenuti: batteria={battery} e liste dei parametri",Pi,pulse,sat,"\n")
      r=self.analyzer.Pulse(ID_P,Pi,pulse,sat,battery)
      for alert in r:
        to_pub=self.__alert
        to_pub["alert"]=alert
        #to_pub["time"]=time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
        to_pub["time"]=datetime.now().replace(microsecond=0).isoformat(' ')
        # Publish alert
        self.client.myPublish(self.__base_topic_pub+ID_P,to_pub)

if __name__=="__main__":
  F=Patient_Monitor_client()
  F.updateService()
  #while True:
    #pass