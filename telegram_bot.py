from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import Update
import MyMQTT
import logging
import requests
import json

users = {190657895: "SuperUser"}
patient_catalog = []

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

#@singleton
class SmartClinicBot(object):

    ADD_PATIENT = 2
    EDIT_PATIENT = 3
    DELETE_PATIENT = 4
    SET_ROOM_TEMPERATURE = 5
    GET_ROOM_TEMPERATURE = 6
    START_WORK = 7
    END_WORK = 8
    GET_SENSOR_BATTERY = 9
    hello = 2

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
        start_handler = CommandHandler('start', self.__start)
        dispatcher.add_handler(start_handler)
        conversation_handler = ConversationHandler(
            entry_points=[
                CommandHandler('add_patient', self.__add_patient)  #,
        #            CommandHandler('edit_patient', self.__edit_patient),
        #            CommandHandler('delete_patient', self.__delete_patient),
        #            CommandHandler('set_room_temperature', self.__set_room_temperature),
        #            CommandHandler('get_room_temperature', self.__get_room_temperature),
        #            CommandHandler('start_work', self.__start_work),
        #            CommandHandler('end_work', self.__end_work),
        #            CommandHandler('get_sensor_battery', self.__get_sensor_battery)
            ],
            states={ 
                SmartClinicBot.ADD_PATIENT: [MessageHandler(Filters.text, self.__insert_patient)]  #, 
        #            SmartClinicBot.EDIT_PATIENT: [], 
        #            SmartClinicBot.DELETE_PATIENT: [],
        #            SmartClinicBot.SET_ROOM_TEMPERATURE: [], 
        #            SmartClinicBot.GET_ROOM_TEMPERATURE: [], 
        #            SmartClinicBot.START_WORK: [],
        #            SmartClinicBot.END_WORK: [], 
        #            SmartClinicBot.GET_SENSOR_BATTERY: []
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)]
        )
        dispatcher.add_handler(conversation_handler)
        
        # Register the Bot to the Service Registry System TODO INTEGRATE
        #r = requests.post(self.__config_settings['host'] + "/add-service",data = json.dumps({
        #    'serviceID' : self.__config_settings['serviceID'],
        #    'name' : self.__config_settings['name']
        #}))
        #while r.status_code != requests.codes.ok:
        #    r = requests.post(self.__config_settings['host'] + "/add-service",data = json.dumps({
        #    'serviceID' : self.__config_settings['serviceID'],
        #    'name' : self.__config_settings['name']
        #    }))

        # Initialize the MQTT Client TODO INTEGRATE
        #r = requests.get(self.__config_settings['host'] + "/message-broker")
        #while r.status_code != requests.codes.ok:
        #    r = requests.get(self.__config_settings['host'] + "/message-broker")
        #message_broker = r.json()
        #self.mqttClient = MyMQTT(self.__config_settings['name'], message_broker['name'], message_broker['port'], self)

    # Start the Bot
    def launch(self):
        self.__updater.start_polling()

    # Receive Notifications from the MQTT Client (i.e. Alarms)
    def notify(self, topic, payload):
        pass

    # Stop the Bot
    def stop(self):
        self.__updater.stop()

    # Method for Authentication and Authorization
    def __check_authZ_authN(self, update, command, userID):
        # Retrieve the list of recognized Users TODO INTEGRATE WITH DEVICE REGISTRY SYSTEM
        #request = requests.get(self.__config_settings['host'+ "/telegram-chat-id-list"])
        #while request.status_code != requests.codes.ok:
        #    request = requests.get(self.__config_settings['host'+ "/telegram-chat-id-list"])
        #users = request.json()['userIDs']
        # Check if the User is among those recognized
        if userID not in users.keys():
            update.message.reply_text("Authentication failed!")
            return False
        # Check if the User has a suitable role for the task to perform
        user_role = users[userID]
        config_tasks = self.__config_settings['tasks']
        for task in config_tasks:
            if task['command'] == command:
                authz_roles = task['roles']
                if user_role in authz_roles:
                    return True
                else: 
                   update.message.reply_text("Authorization failed!") 
                   return False
        return False #default bhv

    def __start(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        update.message.reply_text("Welcome to the SmartClinicBot!")
        # Retrieve the list of recognized Users TODO INTEGRATE WITH DEVICE REGISTRY SYSTEM
        #request = requests.get(self.__config_settings['host'+ "/telegram-chat-id-list"])
        #while request.status_code is not requests.codes.ok:
        #    request = requests.get(self.__config_settings['host'+ "/telegram-chat-id-list"])
        #userID_list = request.json()['userIDs']
        # Check if the User is among those recognized
        if self.__check_authZ_authN(update, 'start', userID):
            update.message.reply_text("Congratulations! You're in!")
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
        
    
    def __add_patient(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'start', userID):
            update.message.reply_text(
                "To insert a new Patient, insert the following data in the following format:\n" \
                "name - <insert_name>\n" \
                "surname - <insert_surname>\n" \
                "age - <insert_age>\n" \
                "description - <insert_description>")
            return self.ADD_PATIENT
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __insert_patient(self, update: Update, context: CallbackContext):
        # Define a Patient from the User Data
        text_entries = (update.message.text.split("\n"))
        try:
            patient = {}
            #for entry in text_entries:
            #    entry_list = entry.split("-")
            #    entry_key = entry_list[0].strip()
            #    entry_value = entry_list[1].strip()
            #    patient[entry_key] = entry_value
            #print(patient.len())
            #if patient.len() != 4:
            #    raise Exception
        except:
            update.message.reply_text("Sorry, this Patient description is invalid.\nCommand aborted")
            return ConversationHandler.END

        # Take the current Patient Catalog and check whether the Patient is already present
        #print(patient_catalog)
        
        # If the Patient is already present, abort the operation; otherwise, insert it in the Patient Catalog
        return ConversationHandler.END

    def __edit_patient(self, update: Update, context: CallbackContext):
        pass
        return SmartClinicBot.EDIT_PATIENT

    def __delete_patient(self, update: Update, context: CallbackContext):
        pass
        return SmartClinicBot.DELETE_PATIENT

    def __set_room_temperature(self, update: Update, context: CallbackContext):
        pass
        return SmartClinicBot.SET_ROOM_TEMPERATURE

    def __get_room_temperature(self, update: Update, context: CallbackContext):
        pass
        return SmartClinicBot.GET_ROOM_TEMPERATURE

    def __start_work(self, update: Update, context: CallbackContext):
        pass
        return SmartClinicBot.START_WORK

    def __end_work(update: Update, context: CallbackContext):
        pass
        return SmartClinicBot.END_WORK

    def __get_sensor_battery(update: Update, context: CallbackContext):
        pass
        return SmartClinicBot.GET_SENSOR_BATTERY

    def __cancel(update: Update, context: CallbackContext):
        update.message.reply_text("Command aborted!")
        return ConversationHandler.END

if __name__ == '__main__':

    bot = SmartClinicBot()
    bot.launch()

    
