from click import edit
from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import Update
import MyMQTT
import logging
import requests
import json

users = {190657895: "SuperUser"}
patientCatalog = { 'patientCatalog':[] }

def singleton(cls):
    instances = {}
    def getinstance():
        if cls not in instances:
            instances[cls] = cls()
        return instances[cls]
    return getinstance

#@singleton
class SmartClinicBot(object):

    ADD_PATIENT = 1
    EDIT_PATIENT_1 = 2
    EDIT_PATIENT_2 = 3
    DELETE_PATIENT_1 = 4
    DELETE_PATIENT_2 = 5
    SET_ROOM_TEMPERATURE = 6
    GET_ROOM_TEMPERATURE = 7
    START_WORK = 8
    END_WORK = 9
    GET_SENSOR_BATTERY = 10

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
        add_patient_handler = ConversationHandler(
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
                SmartClinicBot.ADD_PATIENT: [MessageHandler(Filters.text & ~(Filters.command), self.__add_request_handle)]  #, 
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
        dispatcher.add_handler(add_patient_handler)

        edit_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('edit_patient', self.__edit_patient)
            ],
            states={ 
                SmartClinicBot.EDIT_PATIENT_1: [MessageHandler(Filters.text & ~(Filters.command), self.__patient_search)],
                SmartClinicBot.EDIT_PATIENT_2: [MessageHandler(Filters.text & ~(Filters.command), self.__edit_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(edit_patient_handler)

        delete_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('delete_patient', self.__delete_patient)
            ],
            states={ 
                SmartClinicBot.DELETE_PATIENT_1: [MessageHandler(Filters.text & ~(Filters.command), self.__patient_search)],
                SmartClinicBot.DELETE_PATIENT_2: [MessageHandler(Filters.text & ~(Filters.command), self.__delete_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(delete_patient_handler)
        
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

    @staticmethod
    def __parse_patient(text):
        text_entries = text.split("\n")
        patient = {}
        for entry in text_entries:
            entry_list = entry.split("-")
            if len(entry_list) != 2:
                raise Exception("A key does not have a corresponding value or viceversa")
            entry_key = entry_list[0].strip()
            entry_value = entry_list[1].strip()         
            patient[entry_key] = entry_value
        return patient

    def __add_patient(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'start', userID):
            update.message.reply_text(
                "To insert a new Patient, insert the following data in the following format:\n"
                "patientID - <insert_patientID>\n" 
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                "age - <insert_age>\n"
                "description - <insert_description>")
            context.chat_data['command'] = 'add'
            return SmartClinicBot.ADD_PATIENT
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __add_request_handle(self, update: Update, context: CallbackContext):
        # Define a Patient from the User Data
        try:
            new_patient = SmartClinicBot.__parse_patient(update.message.text)
            # Check if you have fetched the correct number of elements
            if len(new_patient.keys()) != 5:
                raise Exception("Incorrect number of elements")
            # Check if all the excepted keys are present
            if 'name' not in new_patient.keys() or 'patientID'   not in new_patient.keys() or 'surname' not in new_patient.keys() or \
                'age' not in new_patient.keys() or 'description' not in new_patient.keys():
                raise Exception("Missing key")
            # Treat the patientID as a number
            new_patient['patientID'] = int(new_patient['patientID'])
            # Check that both the name and the surname contain alphabetic chars only
            if not new_patient['name'].isalpha() or not new_patient['surname'].isalpha():
                raise Exception("Patient Name/Surname is not alphabetic")
            # Treat the age as a number
            new_patient['age'] = int(new_patient['age'])
        except Exception as e:
            update.message.reply_text(
                "Sorry, this Patient description is invalid.\n"
                "Please, use the following syntax:\n"
                "patientID - <insert_patientID>\n" 
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                "age - <insert_age>\n"
                "description - <insert_description>")
            print(e)
            return SmartClinicBot.ADD_PATIENT

        # Take the current Patient Catalog and check whether the Patient is already present TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM
        patient_catalog = patientCatalog['patientCatalog']
        #print(patient_catalog)
        try:
            # Check if the Patient is already present
            patient_duplicate = False
            for patient in patient_catalog:
                if  patient['patientID'] == new_patient['patientID']:
                    patient_duplicate = True
            # If the Patient is already present, abort the operation; otherwise, insert it in the Patient Catalog
            if patient_duplicate:
                raise Exception("Duplicate Patient")
            else:
                patient_catalog.append(new_patient)
                update.message.reply_text("Patient added successfully!")
                # TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM (use a POST call)
        except Exception as e: #Assumption: all patients in the Patient Catalog are well formatted
            update.message.reply_text("There is already another patient with the same ID.")
            print(e)
            return SmartClinicBot.ADD_PATIENT
        print(patient_catalog)
        return ConversationHandler.END

    def __edit_patient(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'start', userID):
            update.message.reply_text(
                "To edit a Patient, insert their patient ID or their name using the following format:\n"
                "patientID - <insert_patientID>\n" 
                "OR\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                )
            context.chat_data['command'] = 'edit'
            return SmartClinicBot.EDIT_PATIENT_1
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __patient_search(self, update: Update, context: CallbackContext):
        try:
            # Understand which is the current command
            curr_command = context.chat_data['command']
            # Define a Patient from the User Data
            req_patient = SmartClinicBot.__parse_patient(update.message.text)
            # Check if you have fetched the correct number of elements
            # Take the current Patient Catalog and check whether the Patient is already present TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM
            patient_catalog = patientCatalog['patientCatalog']
            # Look for the Patient either by using the PatientID or their name and surname
            patient_present = False
            found_patients = [] 
            if len(req_patient) == 1: # Case in which the User provides the PatientID
                if 'patientID' not in req_patient.keys():
                    raise Exception("Missing key")
                req_patientID = int(req_patient['patientID'])
                for patient in patient_catalog:
                    if patient['patientID'] == req_patientID:
                        patient_present = True
                        found_patients.append(patient)            
            # Case in which the User provides the Name and Surname of the patient
            elif len(req_patient) == 2:
                if 'name' not in req_patient.keys() or 'surname' not in req_patient.keys():
                    raise Exception("Missing key")
                # Check that both the name and the surname contain alphabetic chars only
                if not req_patient['name'].isalpha() or not req_patient['surname'].isalpha():
                    raise Exception("Patient Name/Surname is not alphabetic")
                for patient in patient_catalog:
                    if patient['name'] == req_patient['name'] and patient['surname'] == req_patient['surname']:
                        patient_present = True
                        found_patients.append(patient)
            else:
                raise Exception("Incorrect number of parameters")
                # If the Patient is not present, abort the operation; otherwise, display its data and ask for a new Patient description
            if patient_present:
                if len(found_patients) == 1:
                    found_patient = found_patients.pop()
                    # Store this infomation for when the new Patient description will be provided and the current one will be discarded
                    if curr_command == 'delete':
                        context.chat_data['patientID_to_delete'] = req_patientID
                    elif curr_command == 'edit':
                        context.chat_data['patientID_to_edit'] = req_patientID
                    msg = ("Patient found:\n" +
                        "patientID - {patientID}\n"   .format(patientID=      found_patient['patientID']) +
                        "name - {patientName}\n"      .format(patientName=    found_patient['name']) +
                        "surname - {patientSurname}\n".format(patientSurname= found_patient['surname']) + 
                        "age - {patientAge}\n"        .format(patientAge=     found_patient['age']) +
                        "description - {patientDescription}\n".format(patientDescription=found_patient['description']) +
                        "-"*40 + "\n")
                    if curr_command == 'delete':
                        msg += "Are you sure you want to delete them? [Y/N]"
                    elif curr_command == 'edit':
                        msg += "Redefine the Patient using the same format without patientID"
                    update.message.reply_text(msg) 
                else:
                    msg = "Multiple Patients found!\n"
                    for found_patient in sorted(found_patients, key=lambda p: p['patientID']):
                        msg += "patientID - {patientID}\n".format(patientID=found_patient['patientID']) + \
                            "name - {patientName}\n".format(patientName=found_patient['name']) + \
                            "surname - {patientSurname}\n".format(patientSurname=found_patient['surname']) + \
                            "age - {patientAge}\n".format(patientAge=found_patient['age']) + \
                            "description - {patientDescription}\n".format(patientDescription=found_patient['description']) + \
                            "-"*40 + "\n"
                    msg += "Choose the patient by using their ID with the following format:\n" "patientID - <insert_patientID>" 
                    update.message.reply_text(msg)
                    if curr_command == 'delete':
                        return SmartClinicBot.DELETE_PATIENT_1
                    elif curr_command == 'edit':
                        return SmartClinicBot.EDIT_PATIENT_1             
            else:
                raise Exception("Patient not present")    
            
        except Exception as e:
            update.message.reply_text(
                "Something went wrong. Please use the following format:\n"
                "patientID - <insert_patientID>\n" 
                "OR\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n")
            print(e)
            if curr_command == 'delete':
                return SmartClinicBot.DELETE_PATIENT_1
            elif curr_command == 'edit':
                return SmartClinicBot.EDIT_PATIENT_1 

        if curr_command == 'delete':
            return SmartClinicBot.DELETE_PATIENT_2
        elif curr_command == 'edit':
            return SmartClinicBot.EDIT_PATIENT_2

    def __edit_patient_update(self, update: Update, context: CallbackContext):
        try:
            edited_patient = SmartClinicBot.__parse_patient(update.message.text)
            keys = edited_patient.keys()
            print(edited_patient)
            # Check if you have fetched the correct number of elements
            if len(edited_patient) != 4:
                raise Exception("Incorrect number of elements")
            # Check if all the excepted keys are present
            if 'name' not in keys or 'surname' not in keys or \
                'age' not in keys or 'description' not in keys:
                raise Exception("Missing key")
            # Check that both the name and the surname contain alphabetic chars only
            if not edited_patient['name'].isalpha() or not edited_patient['surname'].isalpha():
                raise Exception("Patient Name/Surname is not alphabetic")
            # Treat the age as a number
            edited_patient['age'] = int(edited_patient['age'])

        except Exception as e:
            update.message.reply_text(
                "Sorry, this Patient description is invalid.\n"
                "Please, use the following format:\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                "age - <insert_age>\n"
                "description - <insert_description>\n")
            print(e)
            # Retry until success
            return SmartClinicBot.EDIT_PATIENT_2
 
        # Insert the PatientID in the edited Patient
        edited_patient['patientID'] = context.chat_data['patientID_to_edit']
        # Take the Patient Catalog TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM
        patient_catalog = patientCatalog['patientCatalog']
        for patient in patient_catalog:
            if patient['patientID'] == edited_patient['patientID']:
                # TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM (USE POST METHOD)
                patient_catalog.remove(patient)
                patient_catalog.append(edited_patient)
                update.message.reply_text("Patient updated successfully!")
                return ConversationHandler.END # terminate asap for better availability
        return ConversationHandler.END

    def __delete_patient(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'start', userID):
            update.message.reply_text(
                "To delete a Patient, insert their patient ID or their name using the following format:\n"
                "patientID - <insert_patientID>\n" 
                "OR\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                )
            context.chat_data['command'] = 'delete'
            return SmartClinicBot.DELETE_PATIENT_1
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __delete_patient_update(self, update: Update, context: CallbackContext):
        try:
            text = update.message.text
            # Delete Patient
            if text == 'Y':
                delete_patientID = context.chat_data['patientID_to_delete']
                # Take the Patient Catalog TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM
                patient_catalog = patientCatalog['patientCatalog']
                for patient in patient_catalog:
                    if patient['patientID'] == delete_patientID:
                        # TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM (USE POST METHOD)
                        patient_catalog.remove(patient)
                        update.message.reply_text("Patient removed successfully!")  
                        return ConversationHandler.END # terminate asap for better availability
            # Do not Delete Patient
            elif text == 'N':
                update.message.reply_text("Patient not deleted.\nAbort")
            else:
                raise Exception("Undefined Answer")

        except Exception as e:
            update.message.reply_text("Sorry, Reply with [Y/N]\n")
            print(e)
            # Retry until success
            return SmartClinicBot.DELETE_PATIENT_2
 
        return ConversationHandler.END
 
    def __set_room_temperature(self, update: Update, context: CallbackContext):
        context.chat_data['command'] = 'set_room_temperature'
        pass
        return SmartClinicBot.SET_ROOM_TEMPERATURE

    def __get_room_temperature(self, update: Update, context: CallbackContext):
        context.chat_data['command'] = 'get_room_temperature'
        pass
        return SmartClinicBot.GET_ROOM_TEMPERATURE

    def __start_work(self, update: Update, context: CallbackContext):
        context.chat_data['command'] = 'start_work'        
        pass
        return SmartClinicBot.START_WORK

    def __end_work(self, update: Update, context: CallbackContext):
        context.chat_data['command'] = 'end_work'        
        pass
        return SmartClinicBot.END_WORK

    def __get_sensor_battery(self, update: Update, context: CallbackContext):
        context.chat_data['command'] = 'get_sensor_battery'        
        pass
        return SmartClinicBot.GET_SENSOR_BATTERY

    def __cancel(self, update: Update, context: CallbackContext):
        update.message.reply_text("Command aborted!")
        return ConversationHandler.END

if __name__ == '__main__':
    bot = SmartClinicBot()
    bot.launch()
