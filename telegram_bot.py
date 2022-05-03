from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import Update
import MyMQTT
import logging
import requests
import json

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

@singleton
class SmartClinicBot(object):

    START = 1
    ADD_PATIENT = 2
    EDIT_PATIENT = 3
    DELETE_PATIENT = 4
    SET_ROOM_TEMPERATURE = 5
    GET_ROOM_TEMPERATURE = 6
    START_WORK = 7
    END_WORK = 8
    GET_SENSOR_BATTERY = 9

    def __init__(self):

        # Retrieve the Token from the Config File
        config_file = open('config.json')
        self.__config_settings = json.load(config_file)
        config_file.close()
        bot_token = self.__config_settings['botToken']
        
        # Define Alarm Black List
        self.alarm_black_list = []

        # Define Working Staff List
        self.working_staff = []

        # Create the Updater and the Dispatcher
        self.__updater = Updater(token=bot_token, use_context=True)
        dispatcher = self.__updater.dispatcher

        # Define logging module (for debug)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)
        
        # Add Handlers to the Conversation Handler and then to the Dispatcher
        conversation_handler = ConversationHandler(
            entry_points=[CommandHandler('start', self.__start),
                    CommandHandler('add_patient', self.__add_patient),
                    CommandHandler('edit_patient', self.__edit_patient),
                    CommandHandler('delete_patient', self.__delete_patient),
                    CommandHandler('set_room_temperature', self.__set_room_temperature),
                    CommandHandler('get_room_temperature', self.__get_room_temperature),
                    CommandHandler('start_work', self.__start_work),
                    CommandHandler('end_work', self.__end_work),
                    CommandHandler('get_sensor_battery', self.__get_sensor_battery)],
            states={SmartClinicBot.START: [MessageHandler(Filters.text, self.__check_passwd)],
                    SmartClinicBot.ADD_PATIENT: [], 
                    SmartClinicBot.EDIT_PATIENT: [], 
                    SmartClinicBot.DELETE_PATIENT: [],
                    SmartClinicBot.SET_ROOM_TEMPERATURE: [], 
                    SmartClinicBot.GET_ROOM_TEMPERATURE: [], 
                    SmartClinicBot.START_WORK: [],
                    SmartClinicBot.END_WORK: [], 
                    SmartClinicBot.GET_SENSOR_BATTERY: []},
            fallbacks=[CommandHandler('cancel', self.__cancel)]
        )
        dispatcher.add_handler(conversation_handler)
        
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
        update.message.reply_text("Welcome to the SmartClinicBot! Please enter your password.")
        return SmartClinicBot.START
    
    def __check_passwd(self, update: Update, context: CallbackContext):

        # Read passwords from the Device and Registry System
        # passwords = sth

        # Ask for password
        # context.bot.send_message(chat_id=update.effective_chat.id, text="Welcome the SmartClinic Bot! Please enter your password.")

        # Check if the password in the list of accepted passwords

        # If so, remove that password from the list (single use)

        # Otherwise, inform the User of the failure

        # Store the Chat ID of the User and its Role (retrieved from the Device and Registry System)

        # Inform the User of being successfully authenticated

        pass
        return ConversationHandler.END

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

    def __cancel(update: Update, context: CallbackContext):
        update.message.reply_text("Command aborted!")
        return ConversationHandler.END

if __name__ == '__main__':

    bot = SmartClinicBot()
    bot.launch()

    
