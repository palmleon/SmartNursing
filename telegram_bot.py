from telegram.ext import Updater, CallbackContext, CommandHandler
from telegram import Update
import MyMQTT
import logging
import requests
import json

class SmartClinicBot(object):
    def __init__(self):

        # Singleton Pattern TODO

        # Retrieve the Token from the Config File
        config_file = open('config.json')
        self.__config_settings = json.load(config_file)
        config_file.close()
        bot_token = self.__config_settings['botToken']

        # Create the Updater and the Dispatcher
        self.__updater = Updater(token=bot_token, use_context=True)
        dispatcher = self.__updater.dispatcher

        # Define logging module (for debug)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)
        
        # Define Command Handlers
        start_handler = CommandHandler('start', self.__start)
        add_patient_handler = CommandHandler('add_patient', self.__add_patient)
        edit_patient_handler = CommandHandler('edit_patient', self.__edit_patient)
        delete_patient_handler = CommandHandler('delete_patient', self.__delete_patient)
        set_room_temperature_handler = CommandHandler('set_room_temperature', self.__set_room_temperature)
        get_room_temperature_handler = CommandHandler('get_room_temperature', self.__get_room_temperature)
        start_work_handler = CommandHandler('start_work', self.__start_work)
        end_work_handler = CommandHandler('end_work', self.__end_work)
        get_sensor_battery_handler = CommandHandler('get_sensor_battery', self.__get_sensor_battery)
        
        # Add Handlers to the Dispatcher
        dispatcher.add_handler(start_handler)
        dispatcher.add_handler(add_patient_handler)
        dispatcher.add_handler(edit_patient_handler)
        dispatcher.add_handler(delete_patient_handler)
        dispatcher.add_handler(set_room_temperature_handler)
        dispatcher.add_handler(get_room_temperature_handler)
        dispatcher.add_handler(start_work_handler)
        dispatcher.add_handler(end_work_handler)
        dispatcher.add_handler(get_sensor_battery_handler)
        
        # Register the Bot to the Service Registry System
        r = requests.post(self.__config_settings['host'] + "/add-service",data = json.dumps({
            'serviceID' : self.__config_settings['serviceID'],
            'name' : self.__config_settings['name']
        }))
        while r.status_code is not requests.codes.ok:
            r = requests.post(self.__config_settings['host'] + "/add-service",data = json.dumps({
            'serviceID' : self.__config_settings['serviceID'],
            'name' : self.__config_settings['name']
            }))

        # Initialize the MQTT Client
        r = requests.get(self.__config_settings['host'] + "/message-broker")
        while r.status_code is not requests.codes.ok:
            r = requests.get(self.__config_settings['host'] + "/message-broker")
        message_broker = r.json()
        self.mqttClient = MyMQTT(self.__config_settings['name'], message_broker['name'], message_broker['port'], self)

    def launch(self):
        self.updater.start_polling()

    def stop(self):
        self.updater.stop()

    def __start(self, update: Update, context: CallbackContext):
        pass
    
    def __add_patient(self, update: Update, context: CallbackContext):
        pass

    def __edit_patient(self, update: Update, context: CallbackContext):
        pass

    def __delete_patient(self, update: Update, context: CallbackContext):
        pass

    def __set_room_temperature(self, update: Update, context: CallbackContext):
        pass

    def __get_room_temperature(self, update: Update, context: CallbackContext):
        pass

    def __start_work(self, update: Update, context: CallbackContext):
        pass

    def __end_work(update: Update, context: CallbackContext):
        pass

    def __get_sensor_battery(update: Update, context: CallbackContext):
        pass

if __name__ == '__main__':

    bot = SmartClinicBot()
    bot.launch()

    
