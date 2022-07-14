import paho.mqtt.client as PahoMQTT
import json
class MyMQTT:
    def __init__(self, clientID, broker, port, notifier):
        #topics è nella forma di lista di tuple (topic,qos)
        self.broker = broker
        self.port = port
        self.notifier = notifier
        self.clientID = clientID
        self._topic = []
        self._isSubscriber = False
        # create an instance of paho.mqtt.client
        self._paho_mqtt = PahoMQTT.Client(clientID,True)  
        # register the callback
        self._paho_mqtt.on_connect = self.myOnConnect
        self._paho_mqtt.on_message = self.myOnMessageReceived
 
 
    def myOnConnect (self, paho_mqtt, userdata, flags, rc):
        print ("Connected to %s with result code: %d" % (self.broker, rc))
        if self._topic!=[]:
            self._paho_mqtt.subscribe(self._topic)
            print(f"\nsubscribing to all topics: {self._topic}\n")



    def myOnMessageReceived (self, paho_mqtt , userdata, msg):
        # A new message is received
        self.notifier.notify (msg.topic, msg.payload)
        
 
    def myPublish (self, topic, msg):
        # publish a message with a certain topic
        self._paho_mqtt.publish(topic, json.dumps(msg), 2)
        print("\nPublished:")
        print(msg)
        print(f"At Topic: {topic}\n")

 
    def mySubscribe (self, topic=None):
        if topic!=None:
            # In questo caso, ho dato in input un topic, quindi si sottoscrive
            # con qos fisso pari a 2
            
            # subscribe for a topic
            self._paho_mqtt.subscribe(topic, 2) 
            # just to remember that it works also as a subscriber
            self._isSubscriber = True
            self._topic.append((topic,2)) # Concatena ai topic a cui è sottoscritto (per tenerne traccia)
            print ("\nsubscribed to %s\n" % (topic))
 
    def start(self):
        #manage connection to broker
        self._paho_mqtt.connect(self.broker , self.port)
        self._paho_mqtt.loop_start()
        
    def unsubscribe(self):
        if (self._isSubscriber):
            #ATTENZIONE attualmente così toglie la sottoscrizione a tutti i Topic
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
            
    def stop (self):
        if (self._isSubscriber):
            # remember to unsuscribe if it is working also as subscriber 
            self._paho_mqtt.unsubscribe(self._topic)
            self._topic=[]
 
        self._paho_mqtt.loop_stop()
        self._paho_mqtt.disconnect()
