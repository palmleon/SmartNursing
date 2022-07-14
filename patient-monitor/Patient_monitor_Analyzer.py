import numpy as np

class Patient_Monitor():
    def __init__(self,messagesdict,thresholdsDict):
        # Alarm messages
        self.__alarm_Tbattery=messagesdict["alarm_Temperature_battery"].split("{}")
        self.__alarm_Tplace=messagesdict["alarm_Temperature_place"].split("{}")
        self.__alarm_Tl=messagesdict["alarm_low_Temperature"].split("{}")
        self.__alarm_Th=messagesdict["alarm_high_Temperature"].split("{}")
        self.__alarm_Pbattery=messagesdict["alarm_Pulse_battery"].split("{}")
        self.__alarm_Pplace=messagesdict["alarm_Pulse_place"].split("{}")
        self.__alarm_Pl=messagesdict["alarm_low_Pulse"].split("{}")
        self.__alarm_Ph=messagesdict["alarm_high_Pulse"].split("{}")
        self.__alarm_Sl=messagesdict["alarm_Saturation_Threshold"].split("{}")
        # Thresholds
        self.__batteryTThreshold = thresholdsDict['battery_Thermometer_threshold']
        self.__highBodyTemperature = thresholdsDict['high_body_temperature']
        self.__lowBodyTemperature = thresholdsDict['low_body_temperature']
        self.__wrongBodyTemperature = thresholdsDict['wrong_body_temperature']
        self.__batteryPThreshold = thresholdsDict['battery_PulseOximeter_threshold']
        self.__attendabilityThreshold = thresholdsDict['attendability_threshold']
        self.__pulseUpper = thresholdsDict['pulse_upper_threshold']
        self.__pulseLower = thresholdsDict['pulse_lower_threshold']
        self.__saturationThreshold = thresholdsDict['saturation_threshold']


    def Temperature(self,ID_P,incoming,battery):
        # Getting one value of temperature and battery each time

        # Checking battery
        if battery<self.__batteryTThreshold:
            alarm=self.__alarm_Tbattery[0]+ID_P+self.__alarm_Tbattery[1]
            #return f"ATTENZIONE, il paziente {ID_P} ha il termometro quasi scarico"
            return alarm

        # Checking if the sample is reliable
        if incoming<=self.__wrongBodyTemperature:
            alarm=self.__alarm_Tplace[0]+ID_P+self.__alarm_Tplace[1]
            return alarm
        # Check for iphotermia condition
        if incoming<self.__lowBodyTemperature:
            alarm=self.__alarm_Tl[0]+ID_P+self.__alarm_Tl[1]+str(incoming)+" C"
            return alarm
        #Check for fever condition
        if incoming>=self.__highBodyTemperature:
            alarm=self.__alarm_Th[0]+ID_P+self.__alarm_Th[1]+str(incoming)+" C"
            return alarm

    def Pulse(self,ID_P,PI,pulse,sat,battery):
        # A set of PI, Pulse and saturation samples coming.
        # One battery value coming.
        alarm=[]
        # Checking battery
        if battery<self.__batteryPThreshold:
            alarm.append(self.__alarm_Pbattery[0]+ID_P+self.__alarm_Pbattery[1])
            return alarm
        # Checking if samples are reliable
        if max(PI)<self.__attendabilityThreshold:
            alarm.append(self.__alarm_Pplace[0]+ID_P+self.__alarm_Pplace[1])
            return alarm

        # Removing not reliable lectures
        to_remove=[]
        for i in range(len(PI)):
            if PI[i]<self.__attendabilityThreshold:
                to_remove.append(i)
        to_remove.sort(reverse=True)
        #print(f"Removed index: {to_remove}")
        for rm in to_remove:
            pulse.pop(rm)
            sat.pop(rm)
        #print(f"Reliable pulse list: {pulse}")
        #print(f"Reliable sat list: {sat}")
        
        pulse=np.mean(pulse)
        sat=np.mean(sat)
        #print(pulse,'pulse computed')

        # Check for hypoxia condition
        if sat<=self.__saturationThreshold:
            alarm.append(self.__alarm_Sl[0]+ID_P+self.__alarm_Sl[1]+str(sat)+" %")
        # Check for low heart rate condition
        if pulse<self.__pulseLower:
            alarm.append(self.__alarm_Pl[0]+ID_P+self.__alarm_Pl[1]+str(pulse)+" bpm")
        # Check for high heart rate condition
        elif pulse>self.__pulseUpper:
            alarm.append(self.__alarm_Ph[0]+ID_P+self.__alarm_Ph[1]+str(pulse)+" bpm")

        return alarm