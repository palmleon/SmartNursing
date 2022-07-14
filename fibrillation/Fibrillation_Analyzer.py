import numpy as np

class Fibrillation_Monitor():
    def __init__(self,messagesdict,thresholdsDict):
        # Alarm messages
        self.__alarm_battery=messagesdict["alarm_battery"].split("{}")
        self.__alarm_place=messagesdict["alarm_place"].split("{}")
        self.__alarm_fibrillation=messagesdict["alarm_fibrillation"].split("{}")
        # Thresholds
        self.__batteryThreshold = thresholdsDict["battery_threshold"]
        self.__fibrillationState = thresholdsDict["fibrillation_std_threshold"]
        self.__attendabilityThreshold = thresholdsDict["attendability_threshold"]
    
    def fibrillation(self,ID_P,PI,pulse,battery):
        # A set of PI and Pulse samples coming.
        # One battery value coming.

        # Checking battery
        if battery<self.__batteryThreshold :
            alarm=self.__alarm_battery[0]+ID_P+self.__alarm_battery[1]
            return alarm
        
        # Checking if there are reliable lectures
        if max(PI)<self.__attendabilityThreshold:
            alarm=self.__alarm_place[0]+ID_P+self.__alarm_place[1]
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
        #print(f"Reliable pulse list: {pulse}")

        # If too much not reliable lectures arrived, the std is not computed
        if len(pulse)<int(len(PI)/2):
            alarm=self.__alarm_place[0]+ID_P+self.__alarm_place[1]
            return alarm
        
        # Computing std on reliable lectures
        pulse=np.std(pulse)
        # Checking std for fibrillation condition
        if pulse>self.__fibrillationState:
            alarm=self.__alarm_fibrillation[0]+ID_P+self.__alarm_fibrillation[1]
            return alarm