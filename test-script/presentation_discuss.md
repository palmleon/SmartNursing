### Discussion

Hello and welcome to the smart clinic video demo.
Smart clinic allows to manage the rooms of a nursing home, setting the temperature of the patient s and common rooms, and settting the luminosity of the patient s room. Smart Clinic collect and analyses patients data, like the body temperature and the pulse rate, notifiyng nurses during the night in case of anomalies like patient in a fibbrillation state or in hipoxia. 
This is the structure of our platform:
Nurses and Doctors can interacts through telegram, nurses will recervice alerts and doctor can manage patients. Doctors can see patient s data statistycs through the thinkspeak dashboard.
Raspberry emulator sends patients and rooms data to the microservices. In our implementation, since we emulate data, this will generate data for all the patients and rooms we add. 

Now I will run the system, I wil use the cmake that builds the images and through a docker compose will run the images.
Let's start opening telgram bot. There are 3 possibles users, Nurses, Docotr, and Superuser that has the permission of both, so I can manage patients and recevice notifications. I will login and start work, that is a feature....

As we can see from the catalog, we have already a room, in which I will add a patient. I can search for it.

To see some behaviour and output of the microservices, I  will run a script that will send specific data to the microservices in order to emulate a particolar condition.

VARI CASI CON DIAGRAMMI DI FLUSSO

1 I will simulate a temperature of 27° during summer in a patient room during an expected presence, so I will recevicve the command actuation ....
2 I will simulate a temperature of 24 °C in a common room in summer during an unexpected presence and without patients in the room. I expect that...
3 I will simulate a case when the patient is in the room, the actuation command will depend on the wheater condition in the city of the nursing home, in our case Turin. The microservice will receive that data and since ... I expect that the luminosity percentage is...
4 Now I will start emulate data for a patient with the id 1. Each time a send value, I send the last 10 sample collected from each sensor.  Fisrt I will emulate a sensor with a low battery level, in order to recevicve the alert
5 Now I will emulate a body temperature for the patient 1 of 39 °C
6 Now I will emulate a fibrillartion state, fibrillation is computed like this, it takes the last n measurments and computing the standard deviation of the attendable measures, check if it is over a certain thereshold 
7 Now I emulate a bad position sensor, since the perfusion index values are under a certain attendability theresold
8 I emulatye a low pulse rate, look at the pulse rate, where the mean is under a certain thereshold
9 Now I emulate a case of hypoxia, the microservices detect it analyzing the values of this vector. 

Untill now, I used data prepared appostely to generate events, Now, I will open the raspberry emulator, that allows me to generate data for patients and rooms every n seconds, and that in the real life corresponds to attach sensor to the patient and the raspberry, and start colleting data. I will now add the patient 1 in the room 1, like in the real life, a new patient identified by id 1 is arrived in the room1. now as we can see, this will generate data for that patient and for that room.

The microservices patient device analyzer, that I have not started intentionally, will check if each patient have all the sensors attached, if not will send a notification. To detach sensor to the patient I can remove the patient from the raspberry emulator, that means in the real life, unplug the sensor. Now the device-connector will not update the devices of the patient 1 and the microservices will detect it.

In the meanwhile the device and registry system, all services and devices have beeing registered and updating to the device and registry system, that checks and delete from the list services and devices not updated. For example thorugh this API I can see al devices currently active.

There is also another microservices, the terminal, that allows to add rooms and users in the system. For example now I will create a new room.

To conclude, I will go to the thinkspeak dasshboard as Doctor, and I can see that for the patient 1 data are collected and several graph are proposed like.....

Before conclude, I will notify telegram that I have finished my work for today, so I end work and I will no more receivce notifications.

Thanks for the attention.