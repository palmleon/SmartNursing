from Fibrillation_Analyzer import *
from MyMQTT import MyMQTT
import time
import json
import requests

class Fibrillation_Monitor_client():
  def __init__(self):
    # Reading configuration file
    fp=open('Fibrillation_config.json')
    conf_file = json.load(fp)
    fp.close()
    # Getting service Id, service name and registry host
    self.__clientID=conf_file["serviceID"]
    self.__name=conf_file["name"]
    self.__register=conf_file["host"]
    # Getting service update time
    self.__update_service_time_seconds = conf_file["update_service_time_seconds"]
    # Getting alarm template and messages
    self.__alert=conf_file["template_alarm"]
    messagesdict=conf_file["alarm_messages"]
    # Getting Thresholds
    ThresholdsDict=conf_file["Thresholds"]
    # Registration
    r = requests.post(self.__register+"/add-service",data= json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))

    # Request for broker information
    r = requests.get(self.__register+"/message-broker")
    mb = r.json()
    self.__broker=mb['name']
    self.__port=mb['port']
    # Request for subscibe and publish base topics
    r = requests.get(self.__register+"/patient-saturation-base-topic")
    mb = r.json()
    self.__topic_sub=mb+"+"

    r = requests.get(self.__register+"/alarm-base-topic")
    mb = r.json()
    self.__base_topic_pub=mb

    # Creating analyzer
    self.analyzer=Fibrillation_Monitor(messagesdict,ThresholdsDict)

    # Creating client
    self.client = MyMQTT(self.__name, self.__broker, self.__port, self)

    # Starting client
    self.client.start()
    time.sleep(2)

    # Subscribing
    self.client.mySubscribe(self.__topic_sub)
  
  def updateService(self) :
    while True :
      time.sleep(self.__update_service_time_seconds)
      r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__clientID, "name" : self.__name}))
      #print("Updating service")

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
    for ev in evento:
      if ev["n"]=="battery":
        battery=ev["v"]

      if ev["n"]=="perfusion index":
        Pi=ev["v"]
      
      if ev["n"]=="pulse rate":
        pulse=ev["v"]
    
    if len(Pi)>1:
      r=self.analyzer.fibrillation(ID_P,Pi,pulse,battery)
      if r!=None:
        to_pub=self.__alert
        to_pub["alert"]=r
        to_pub["time"]=time.strftime('%Y/%m/%d %H:%M:%S', time.localtime())
        # Publish alert
        self.client.myPublish(self.__base_topic_pub+ID_P,to_pub)

if __name__=="__main__":
  F=Fibrillation_Monitor_client()
  F.updateService()
  #while True:
    #pass