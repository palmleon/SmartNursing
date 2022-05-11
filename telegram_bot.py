from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import Update
from MyMQTT import MyMQTT
import logging
import requests
import json
from time import time

users = {190657895: "SuperUser"}
patientCatalog = { 'patientCatalog':[] }
rooms = {1: {"desired-temperature": 23},
         2: {"desired-temperature": 9},
         3: {"desired-temperature": 24}}

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
    SEARCH_PATIENT = 6
    SET_ROOM_TEMPERATURE = 7
    GET_ROOM_TEMPERATURE = 8
    GET_SENSOR_BATTERY = 9

    def __init__(self):

        # Retrieve the Token from the Config File
        config_file = open('config.json')
        self.__config_settings = json.load(config_file)
        config_file.close()
        bot_token = self.__config_settings['botToken']
        
        # Define Alarm Black List
        self.__alarm_black_list = {
            'alarms': [],
            'last_update': int(time())
        }

        # Define Working Staff List
        self.__working_staff = {}

        # Create the Updater and the Dispatcher
        self.__updater = Updater(token=bot_token, use_context=True)
        dispatcher = self.__updater.dispatcher

        # Define logging module (for debug)
        logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            level=logging.INFO)
 
        # Define Handlers and add them to the Dispatcher
        start_handler = CommandHandler('start', self.__start)
        dispatcher.add_handler(start_handler)

        add_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('add_patient', self.__add_patient_entry)
            ],
            states={ 
                SmartClinicBot.ADD_PATIENT: [MessageHandler(Filters.text & ~(Filters.command), self.__add_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)]
        )
        dispatcher.add_handler(add_patient_handler)

        edit_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('edit_patient', self.__edit_patient_entry)
            ],
            states={ 
                SmartClinicBot.EDIT_PATIENT_1: [MessageHandler(Filters.text & ~(Filters.command), self.__search_patient)],
                SmartClinicBot.EDIT_PATIENT_2: [MessageHandler(Filters.text & ~(Filters.command), self.__edit_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(edit_patient_handler)

        delete_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('delete_patient', self.__delete_patient_entry)
            ],
            states={ 
                SmartClinicBot.DELETE_PATIENT_1: [MessageHandler(Filters.text & ~(Filters.command), self.__search_patient)],
                SmartClinicBot.DELETE_PATIENT_2: [MessageHandler(Filters.text & ~(Filters.command), self.__delete_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(delete_patient_handler)

        search_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('search_patient', self.__search_patient_entry)
            ],
            states={ 
                SmartClinicBot.SEARCH_PATIENT: [MessageHandler(Filters.text & ~(Filters.command), self.__search_patient)],
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(search_patient_handler)

        show_patients_handler = CommandHandler('show_patients', self.__show_patients)
        dispatcher.add_handler(show_patients_handler)

        get_room_temperature_handler = ConversationHandler(
            entry_points=[
                CommandHandler('get_room_temperature', self.__get_room_temperature_entry)
            ],
            states={ 
                SmartClinicBot.GET_ROOM_TEMPERATURE: [MessageHandler(Filters.text & ~(Filters.command), self.__get_room_temperature)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(get_room_temperature_handler)

        start_work_handler = CommandHandler('start_work', self.__start_work)
        dispatcher.add_handler(start_work_handler)

        end_work_handler = CommandHandler('end_work', self.__end_work)
        dispatcher.add_handler(end_work_handler)

        # Extract info about the MQTT Broker from the Device and Registry System TODO UNCOMMENT WHEN INTEGRATING WITH DEVICE AND REGISTRY SYSTEM
        #r = requests.get(self.__config_settings['host'] + "/message-broker")
        #while r.status_code != requests.codes.ok:
        #    r = requests.get(self.__config_settings['host'] + "/message-broker")
        #message_broker = r.json()
        message_broker = {}
        message_broker['name'] = 'localhost'
        message_broker['port'] = 1883

        # Initialize the MQTT Client for Patient Alarm TODO INTEGRATE
        self.__mqttPatientClient = MyMQTT(self.__config_settings['mqttClientName-Patient'], message_broker['name'], message_broker['port'], self)
        
        # Initialize the MQTT Client for Room Alarm TODO INTEGRATE
        self.__mqttRoomClient = MyMQTT(self.__config_settings['mqttClientName-Room'], message_broker['name'], message_broker['port'], self)
        
    # Start the Bot
    def launch(self):

        # Extract info about the MQTT Topics for Patient Alarms and Room Alarms TODO UNCOMMENT WHEN INTEGRATING WITH DEVICE AND REGISTRY SYSTEM
        #r = requests.get(self.__config_settings['host'] + "/alarm-base-topic")
        #while r.status_code != requests.codes.ok:
        #    r = requests.get(self.__config_settings['host'] + "/alarm-base-topic")
        #patient_topic = r.json()
        patient_topic = 'group01/IoTProject/PatientAlarm/+'

        #r = requests.get(self.__config_settings['host'] + "/alarm-room-topic")
        #while r.status_code != requests.codes.ok:
        #    r = requests.get(self.__config_settings['host'] + "/alarm-room-topic")
        #room_topic = r.json()
        room_topic = 'group01/IoTProject/RoomAlarm/+'

        self.__updater.start_polling()
        self.__mqttPatientClient.start()
        self.__mqttPatientClient.mySubscribe(patient_topic)
        self.__mqttRoomClient.start()
        self.__mqttRoomClient.mySubscribe(room_topic)
        
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

   # Stop the Bot
    def stop(self):
        self.__mqttRoomClient.unsubscribe()
        self.__mqttRoomClient.stop()
        self.__mqttPatientClient.unsubscribe()
        self.__mqttPatientClient.stop()
        self.__updater.stop()

    # Receive Notifications from the MQTT Client (i.e. Alarms)
    # The topic contains the ID of the Patient/Room
    # The Payload is a raw string, encoded in utf-8
    def notify(self, topic, payload):
        
        try:
            # Extract the kind of topic and the ID
            topics = topic.split('/')
            if topics[-2] == 'PatientAlarm':
                alarm_type = 'PATIENT'
            elif topics[-2] == 'RoomAlarm':
                alarm_type = 'ROOM'
            id = int(topics[-1]) # POSSIBLE ERROR

            # Extract the payload
            msg = payload.decode('utf-8') # POSSIBLE ERROR
            #print('Hello from MQTT! Topic: ' + topic + ", Payload: " + msg)

            # Construct an Alarm object
            new_alarm = {}
            new_alarm['alarm_type'] = alarm_type
            new_alarm['msg'] = msg
            new_alarm['id'] = id
            new_alarm['timestamp'] = int(time())
            #print(new_alarm['timestamp'])

            # Check if the current message is in the Black List and the message has been sent < 1 minutes before
            alarm_black_list = self.__alarm_black_list['alarms']
            already_sent = False
            found = False
            for alarm in alarm_black_list:
                if alarm['alarm_type'] == new_alarm['alarm_type'] and alarm['id'] == new_alarm['id'] and alarm['msg'] == new_alarm['msg']:
                    found = True
                    if new_alarm['timestamp'] - alarm['timestamp'] < 60:
                        already_sent = True
                        #print("Alarm already sent " + str(new_alarm['timestamp'] - alarm['timestamp']) + "s ago!")
                    else: # Remove the alarm since it will be reuploaded
                        alarm_index = alarm_black_list.index(alarm)
            if found and not already_sent:
                alarm_black_list.pop(alarm_index)

            # If that is the case, do not forward it; 
            # otherwise, forward the alarm to all the staff that is currently working and update the Black List about this alarm
            if not already_sent:                
                
                for chatID in self.__working_staff.values():
                    # TODO ADD WARNING SIGNS
                    text = "\u26a0 " + new_alarm['alarm_type'] + " ALARM \u26a0\n" + \
                        new_alarm['alarm_type'] + " " + str(new_alarm['id']) + ": " + new_alarm['msg']
                    #NOTE: protect_content is True for privacy reasons (no information leakage outside of the actors involved)
                    self.__updater.bot.send_message(chat_id=chatID, text=text, protect_content=True)
                
                # Update the Black List
                alarm_black_list.append(new_alarm)

            # If more than 5 minutes have spent since the last update, update the Black List
            curr_time = int(time())
            last_update = self.__alarm_black_list['last_update']    

            if curr_time - last_update > 300:
                  
                alarm_black_list = [alarm for alarm in alarm_black_list if curr_time - alarm['timestamp'] < 60]
                self.__alarm_black_list['last_update'] = curr_time

            self.__alarm_black_list['alarms'] = alarm_black_list
            #print(self.__alarm_black_list['alarms'])
            #print(self.__alarm_black_list['last_update'])

        except Exception as e:
            print("Exception found")
            print(e)


    # Method for Authentication and Authorization
    def __check_authZ_authN(self, update, command, userID):
        # Retrieve the list of recognized Users TODO INTEGRATE WITH DEVICE REGISTRY SYSTEM
        #request = requests.get(self.__config_settings['host'+ "/telegram-chat-id-list"])
        #while request.status_code != requests.codes.ok:
        #    request = requests.get(self.__config_settings['host'+ "/telegram-chat-id-list"])
        #users = request.json()['userIDs']
        # Check if the User is among those recognized
        if userID not in users:
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
            update.message.reply_text("Your user ID: " + str(update.effective_chat.id))
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")

    @staticmethod
    def __parse_input(text):
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

    def __add_patient_entry(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'add_patient', userID):
            context.chat_data['command'] = 'add_patients'
            update.message.reply_text(
                "To insert a new Patient, insert the following data in the following format:\n"
                "patientID - <insert_patientID>\n" 
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                "age - <insert_age>\n"
                "description - <insert_description>")
            return SmartClinicBot.ADD_PATIENT
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __add_patient_update(self, update: Update, context: CallbackContext):
        # Define a Patient from the User Data
        try:
            new_patient = SmartClinicBot.__parse_input(update.message.text)
            # Check if you have fetched the correct number of elements
            if len(new_patient) != 5:
                raise Exception("Incorrect number of elements")
            # Check if all the excepted keys are present
            if 'name' not in new_patient or 'patientID'   not in new_patient or 'surname' not in new_patient or \
                'age' not in new_patient or 'description' not in new_patient:
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

    def __edit_patient_entry(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'edit_patient', userID):
            update.message.reply_text(
                "To edit a Patient, insert their patient ID or their name using the following format:\n"
                "patientID - <insert_patientID>\n" 
                "OR\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                )
            context.chat_data['command'] = 'edit_patient'
            return SmartClinicBot.EDIT_PATIENT_1
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __search_patient(self, update: Update, context: CallbackContext):
        try:
            # Understand which is the current command
            curr_command = context.chat_data['command']
            # Define a Patient from the User Data
            req_patient = SmartClinicBot.__parse_input(update.message.text)
            # Check if you have fetched the correct number of elements
            # Take the current Patient Catalog and check whether the Patient is already present TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM
            patient_catalog = patientCatalog['patientCatalog']
            # Look for the Patient either by using the PatientID or their name and surname
            patient_present = False
            found_patients = [] 
            if len(req_patient) == 1: # Case in which the User provides the PatientID
                if 'patientID' not in req_patient:
                    raise Exception("Missing key")
                req_patientID = int(req_patient['patientID'])
                for patient in patient_catalog:
                    if patient['patientID'] == req_patientID:
                        patient_present = True
                        found_patients.append(patient)            
            # Case in which the User provides the Name and Surname of the patient
            elif len(req_patient) == 2:
                if 'name' not in req_patient or 'surname' not in req_patient:
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
                    if curr_command == 'delete_patient':
                        context.chat_data['patientID_to_delete'] = req_patientID
                    elif curr_command == 'edit_patient':
                        context.chat_data['patientID_to_edit'] = req_patientID
                    msg = ("Patient found:\n" + "-"*40 + "\n" +
                        "patientID - {patientID}\n"   .format(patientID=      found_patient['patientID']) +
                        "name - {patientName}\n"      .format(patientName=    found_patient['name']) +
                        "surname - {patientSurname}\n".format(patientSurname= found_patient['surname']) + 
                        "age - {patientAge}\n"        .format(patientAge=     found_patient['age']) +
                        "description - {patientDescription}\n".format(patientDescription=found_patient['description']))
                    if curr_command == 'delete_patient':
                        msg += "-"*40
                        msg += "Are you sure you want to delete them? [Y/N]"
                    elif curr_command == 'edit_patient':
                        msg += "-"*40
                        msg += "Redefine the Patient using the same format without patientID"
                    update.message.reply_text(msg) 
                else:
                    msg = "Multiple Patients found!\n" + "-"*40 + "\n"
                    for found_patient in sorted(found_patients, key=lambda p: p['patientID']):
                        msg += "patientID - {patientID}\n".format(patientID=found_patient['patientID']) + \
                            "name - {patientName}\n".format(patientName=found_patient['name']) + \
                            "surname - {patientSurname}\n".format(patientSurname=found_patient['surname']) + \
                            "age - {patientAge}\n".format(patientAge=found_patient['age']) + \
                            "description - {patientDescription}\n".format(patientDescription=found_patient['description'])
                    if curr_command == 'delete_patient' or curr_command == 'edit_patient':
                        msg += "-"*40
                        msg += "Choose the patient by using their ID with the following format:\n" "patientID - <insert_patientID>" 
                    update.message.reply_text(msg)
                    if curr_command == 'delete_patient':
                        return SmartClinicBot.DELETE_PATIENT_1
                    elif curr_command == 'edit_patient':
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
            if curr_command == 'delete_patient':
                return SmartClinicBot.DELETE_PATIENT_1
            elif curr_command == 'edit_patient':
                return SmartClinicBot.EDIT_PATIENT_1 
            elif curr_command == 'search_patient':
                return SmartClinicBot.SEARCH_PATIENT

        if curr_command == 'delete_patient':
            return SmartClinicBot.DELETE_PATIENT_2
        elif curr_command == 'edit_patient':
            return SmartClinicBot.EDIT_PATIENT_2
        return ConversationHandler.END #default bhv (also expected behavior for search_patient)

    def __edit_patient_update(self, update: Update, context: CallbackContext):
        try:
            edited_patient = SmartClinicBot.__parse_input(update.message.text)
            #print(edited_patient)
            # Check if you have fetched the correct number of elements
            if len(edited_patient) != 4:
                raise Exception("Incorrect number of elements")
            # Check if all the excepted keys are present
            if 'name' not in edited_patient or 'surname' not in edited_patient or \
                'age' not in edited_patient or 'description' not in edited_patient:
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
            #print(e)
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

    def __delete_patient_entry(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'delete_patient', userID):
            update.message.reply_text(
                "To delete a Patient, insert their patient ID or their name using the following format:\n"
                "patientID - <insert_patientID>\n" 
                "OR\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                )
            context.chat_data['command'] = 'delete_patient'
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
            update.message.reply_text("Sorry, Reply with [Y/N]")
            print(e)
            # Retry until success
            return SmartClinicBot.DELETE_PATIENT_2
 
        return ConversationHandler.END

    def __search_patient_entry(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'search_patient', userID):
            update.message.reply_text(
                "To search a Patient, insert their patient ID or their name using the following format:\n"
                "patientID - <insert_patientID>\n" 
                "OR\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                )
            context.chat_data['command'] = 'search_patient'
            return SmartClinicBot.SEARCH_PATIENT
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __show_patients(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'show_patients', userID):
            context.chat_data['command'] = 'show_patients'
            patient_catalog = patientCatalog['patientCatalog']
            if len(patient_catalog) == 0:
                msg = "No patient found"
            else:
                msg = "Currently registered patients:\n"
                for found_patient in sorted(patient_catalog, key=lambda p: p['patientID']):
                    msg +=  "-"*40 + "\n" + \
                            "patientID - {patientID}\n".format(patientID=found_patient['patientID']) + \
                            "name - {patientName}\n".format(patientName=found_patient['name']) + \
                            "surname - {patientSurname}\n".format(patientSurname=found_patient['surname']) + \
                            "age - {patientAge}\n".format(patientAge=found_patient['age']) + \
                            "description - {patientDescription}\n".format(patientDescription=found_patient['description']) 
            update.message.reply_text(msg)
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
 
    def __set_room_temperature(self, update: Update, context: CallbackContext):
        context.chat_data['command'] = 'set_room_temperature'
        pass
        return SmartClinicBot.SET_ROOM_TEMPERATURE

    def __get_room_temperature_entry(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'get_room_temperature', userID):
            update.message.reply_text(
                "To read the temperature of a room, insert its number using the following format:\n"
                "roomNumber - <insert_roomNumber>"
                )
            context.chat_data['command'] = 'get_room_temperature'
            return SmartClinicBot.GET_ROOM_TEMPERATURE
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __get_room_temperature(self, update: Update, context: CallbackContext):
        try:
            room = SmartClinicBot.__parse_input(update.message.text)
            # Check if you have fetched the correct number of elements
            if len(room) != 1:
                raise Exception("Incorrect number of elements")
            # Check if all the excepted keys are present
            if 'roomNumber' not in room:
                raise Exception("Missing key")
            # Treat the Room Number as an integer
            roomNumber = int(room['roomNumber'])
            # Get the Room info TODO INTEGRATE WITH DEVICE AND REGISTRY SYSTEM
            fetched_room = rooms[roomNumber]
            fetched_room_temp = fetched_room['desired-temperature']
            update.message.reply_text(
                "Room Temperature for Room" + str(roomNumber) + ": " + str(fetched_room_temp)
            )

        except Exception as e:
            update.message.reply_text(
                "Something went wrong. "
                "Please, use the following format:\n"
                "roomNumber - <insert_roomNumber>")
            print(e)
            # Retry until success
            return SmartClinicBot.GET_ROOM_TEMPERATURE

        return ConversationHandler.END

    def __start_work(self, update: Update, context: CallbackContext):
        
        try:
            userID = update.message.from_user.id   
            chatID = update.effective_chat.id

            # Authentication and Authorization
            if self.__check_authZ_authN(update, 'start_work', userID):
                context.chat_data['command'] = 'start_work' 

                # Check if the user has already launched a /start_work command, i.e. they're in the working staff
                if userID not in self.__working_staff:
                    self.__working_staff[userID] = chatID
                    update.message.reply_text("You have been added to the Working Staff!")
                else:
                    raise Exception("You have already started to work!")

            else:
                raise Exception("Authentication/Authorization failed.")

        except Exception as e:
            update.message.reply_text("Something went wrong. Retry")
            print(e)

    def __end_work(self, update: Update, context: CallbackContext):
             
        try:
            userID = update.message.from_user.id   
            
            # Authentication and Authorization
            if self.__check_authZ_authN(update, 'end_work', userID):
                context.chat_data['command'] = 'end_work' 

                # Check if the user has already launched an /end_work command, i.e. they're not in the working staff
                if userID in self.__working_staff:
                    del self.__working_staff[userID]
                    update.message.reply_text("You have been removed from the Working Staff!")
                else:
                    raise Exception("You have already finished to work!")
                    
            else:
                raise Exception("Authentication/Authorization failed.")

        except Exception as e:
            update.message.reply_text("Something went wrong. Retry")
            print(e)

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
