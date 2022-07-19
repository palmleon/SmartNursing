import logging
import requests
import json
from telegram.ext import Updater, CallbackContext, CommandHandler, ConversationHandler, MessageHandler, Filters
from telegram import Update
from MyMQTT import MyMQTT
from TelegramBotExceptions import DuplicatePatientError, ServerNotFoundError, \
   PatientNotFoundError, RoomNotFoundError, ShiftStartedError, ShiftEndedError, TelegramTaskNotFoundError, TelegramUserNotFoundError
from time import sleep, time

class SmartNursingBot(object):

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
        r = requests.get(self.__config_settings['host']+"/bot-token")
        while r.status_code != requests.codes.ok:
            r = requests.get(self.__config_settings['host']+"/bot-token")
        
        bot_token  = r.json()
       
        # Define Alarm Black List
        self.__alarm_black_list = {
            'alarms': [],
            'last_update': int(time())
        }

        # Define Working Staff List
        self.__working_staff = {}

        # Create the Updater and the Dispatcher (the Bot)
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
                SmartNursingBot.ADD_PATIENT: [MessageHandler(Filters.text & ~(Filters.command), self.__add_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)]
        )
        dispatcher.add_handler(add_patient_handler)

        edit_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('edit_patient', self.__edit_patient_entry)
            ],
            states={ 
                SmartNursingBot.EDIT_PATIENT_1: [MessageHandler(Filters.text & ~(Filters.command), self.__search_patient)],
                SmartNursingBot.EDIT_PATIENT_2: [MessageHandler(Filters.text & ~(Filters.command), self.__edit_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(edit_patient_handler)

        delete_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('delete_patient', self.__delete_patient_entry)
            ],
            states={ 
                SmartNursingBot.DELETE_PATIENT_1: [MessageHandler(Filters.text & ~(Filters.command), self.__search_patient)],
                SmartNursingBot.DELETE_PATIENT_2: [MessageHandler(Filters.text & ~(Filters.command), self.__delete_patient_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(delete_patient_handler)

        search_patient_handler = ConversationHandler(
            entry_points=[
                CommandHandler('search_patient', self.__search_patient_entry)
            ],
            states={ 
                SmartNursingBot.SEARCH_PATIENT: [MessageHandler(Filters.text & ~(Filters.command), self.__search_patient)],
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(search_patient_handler)

        show_patients_handler = CommandHandler('show_patients', self.__show_patients)
        dispatcher.add_handler(show_patients_handler)

        set_room_temperature_handler = ConversationHandler(
            entry_points=[
                CommandHandler('set_room_temperature', self.__set_room_temperature_entry)
            ],
            states={ 
                SmartNursingBot.SET_ROOM_TEMPERATURE: [MessageHandler(Filters.text & ~(Filters.command), self.__set_room_temperature_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(set_room_temperature_handler)

        get_room_temperature_handler = ConversationHandler(
            entry_points=[
                CommandHandler('get_room_temperature', self.__get_room_temperature_entry)
            ],
            states={ 
                SmartNursingBot.GET_ROOM_TEMPERATURE: [MessageHandler(Filters.text & ~(Filters.command), self.__get_room_temperature_update)]
            },
            fallbacks=[CommandHandler('cancel', self.__cancel)])
        dispatcher.add_handler(get_room_temperature_handler)

        start_work_handler = CommandHandler('start_work', self.__start_work)
        dispatcher.add_handler(start_work_handler)

        end_work_handler = CommandHandler('end_work', self.__end_work)
        dispatcher.add_handler(end_work_handler)

        r = requests.get(self.__config_settings['host']+"/message-broker")
        while r.status_code != requests.codes.ok:
            r = requests.get(self.__config_settings['host']+"/message-broker")
        mb = r.json()
        message_broker = {}
        message_broker['name'] = mb['name']
        message_broker['port'] = mb['port']

        # Initialize MQTT Client for Patient Alarms
        self.__mqttPatientClient = MyMQTT(self.__config_settings['mqttClientName-Patient'], message_broker['name'], message_broker['port'], self)
        
        # Initialize MQTT Client for Room Alarms
        self.__mqttRoomClient = MyMQTT(self.__config_settings['mqttClientName-Room'], message_broker['name'], message_broker['port'], self)
        
    # Start the Bot
    def launch(self):

        # Extract info about the MQTT Topics for Patient Alarms and Room Alarms 
        r = requests.get(self.__config_settings['host']+"/alarm-base-topic")
        while r.status_code != requests.codes.ok:
            r = requests.get(self.__config_settings['host']+"/alarm-base-topic")
        
        #patient_topic should be something like 'group01/IoTProject/PatientAlarm/+'
        try:
            patient_topic = r.json()+"+"
        except ValueError:
            print("Could not extract MQTT Topics - Abort")
        
        #r = requests.get(self.__config_settings['host'] + "/alarm-room-topic")
        #while r.status_code != requests.codes.ok:
        #    r = requests.get(self.__config_settings['host'] + "/alarm-room-topic")
        #room_topic = r.json()
        #TODO Integrate quando il Topic per Room Alarms sarà definito nel Device and Registry System
        room_topic = 'group01/IoTProject/RoomAlarm/+'

        # Launch the Bot and the MQTT Clients
        self.__updater.start_polling()
        self.__mqttPatientClient.start()
        self.__mqttPatientClient.mySubscribe(patient_topic)
        self.__mqttRoomClient.start()
        self.__mqttRoomClient.mySubscribe(room_topic)
        
        # Register the Bot to the Service Registry System
        
        r = requests.post(self.__config_settings['host'] + "/add-service",data = json.dumps({
            'serviceID' : self.__config_settings['serviceID'],
            'name' : self.__config_settings['name']
        }))
        while r.status_code != requests.codes.ok:
            r = requests.post(self.__config_settings['host'] + "/add-service",data = json.dumps({
            'serviceID' : self.__config_settings['serviceID'],
            'name' : self.__config_settings['name']
            }))

    # Stop the Bot and the MQTT Clients
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
        print("Message received")
        try:
            # Extract the kind of topic and the ID
            topics = topic.split('/')
            if topics[-2] == 'PatientAlarm':
                alarm_type = 'PATIENT'
            elif topics[-2] == 'RoomAlarm':
                alarm_type = 'ROOM'
            id = int(topics[-1])

            # Extract the payload
            msg = json.loads(payload)
           
            # Construct an Alarm object
            new_alarm = {}
            new_alarm['alarm_type'] = alarm_type
            new_alarm['msg'] = "".join([i for i in msg['alert'] if not i.isdigit() and i != '.'])
            new_alarm['localtime'] = msg['time']
            new_alarm['id'] = id
            new_alarm['timestamp'] = int(time())
            #print(new_alarm['timestamp'])

            # Check if the current message is in the Black List and the message has been sent < self.__minIntervalBetweenAlarms seconds before
            alarm_black_list = self.__alarm_black_list['alarms']
            already_sent = False
            found = False
            for alarm in alarm_black_list:
                if alarm['alarm_type'] == new_alarm['alarm_type'] and alarm['id'] == new_alarm['id'] and alarm['msg'] == new_alarm['msg']:
                    found = True
                    if new_alarm['timestamp'] - alarm['timestamp'] < int(self.__config_settings['minIntervalBetweenAlarms']):
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
                    text = "\u26a0 " + new_alarm['alarm_type'] + " ALARM \u26a0\n" + \
                           "[" + new_alarm['localtime'] + "]: " + new_alarm['msg'] 
                    #protect_content is True for privacy reasons (no information leakage outside of the actors involved)
                    self.__updater.bot.send_message(chat_id=chatID, text=text, protect_content=True)
                
                # Update the Black List
                alarm_black_list.append(new_alarm)

            # If more than self.__threasholdBlackListUpdate seconds have spent since the last update, update the Black List
            curr_time = int(time())
            last_update = self.__alarm_black_list['last_update']    

            if curr_time - last_update > int(self.__config_settings['thresholdBlackListUpdate']):
                  
                alarm_black_list = [alarm for alarm in alarm_black_list if curr_time - alarm['timestamp'] < int(self.__config_settings['minIntervalBetweenAlarms'])]
                self.__alarm_black_list['last_update'] = curr_time

            self.__alarm_black_list['alarms'] = alarm_black_list

        except (json.JSONDecodeError, KeyError, ValueError) as e:
            print("The msg is not in the expected format!")
            print(e)
        #except Exception as e:
        #    print("Exception found")
        #    print(e)


    # Method for Authentication and Authorization
    def __check_authZ_authN(self, update, command, userID):
        
        try:
            # Retrieve the list of recognized Users 
            nattempts = 1
            request = requests.get(self.__config_settings['host']+ "/telegram-user/"+str(userID))
            while nattempts < 5 and str(request.status_code).startswith('5'):
                nattempts += 1
                request = requests.get(self.__config_settings['host']+ "/telegram-user/"+str(userID))

            if nattempts == 5 and str(request.status_code).startswith('5'):
                raise ServerNotFoundError
            elif request.status_code != requests.codes.ok:
                raise TelegramUserNotFoundError
            user = request.json()
            
            # Check if the User has a suitable role for the task to perform
            nattempts = 1
            request = requests.get(self.__config_settings['host']+ "/telegram-task/"+command)
            while nattempts < 5 and str(request.status_code).startswith('5'):
                nattempts += 1
                request = requests.get(self.__config_settings['host']+ "/telegram-task/"+command)
            
            if nattempts == 5 and str(request.status_code).startswith('5'):
                raise ServerNotFoundError
            elif request.status_code != requests.codes.ok:
                raise TelegramTaskNotFoundError

            task = request.json()
            roles = task['roles']
            if user['role'] in roles:
                return True
            else: 
                update.message.reply_text("Authorization failed!")

        except json.JSONDecodeError as e:
            update.message.reply_text(
                "Invalid answer from the Host. Abort."
            )
            print(e) 
        except ServerNotFoundError:
            update.message.reply_text("Host unreachable. Abort.")
            print(e)
        except TelegramUserNotFoundError:
            update.message.reply_text("Telegram User not found. Authentication failed!")
            print(e)
        except TelegramTaskNotFoundError:
            update.message.reply_text("Telegram task not found. Abort.")
            print(e)

        return False #default bhv

    def __start(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        update.message.reply_text("Welcome to the SmartNursingBot!")
        # Check if the User is among those recognized
        if self.__check_authZ_authN(update, 'start', userID):
            update.message.reply_text("Congratulations! You're in!")
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")

    @staticmethod
    def __parse_input(text):
        text_entries = text.split("\n")
        patient = {}
        for entry in text_entries:
            entry_list = entry.split("-")
            if len(entry_list) != 2:
                raise ValueError
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
                "roomID - <insert_roomID>\n" 
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                "age - <insert_age>\n"
                "description - <insert_description>")
            return SmartNursingBot.ADD_PATIENT
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __add_patient_update(self, update: Update, context: CallbackContext):
        # Define a Patient from the User Data
        try:
            new_patient = SmartNursingBot.__parse_input(update.message.text)
            # Check if you have fetched the correct number of elements
            if len(new_patient) != 6:
                raise ValueError("Incorrect number of elements")
            # Check if all the excepted keys are present
            if 'name' not in new_patient or 'patientID'   not in new_patient or 'roomID' not in new_patient \
                or 'surname' not in new_patient or 'age' not in new_patient or 'description' not in new_patient:
                raise ValueError("Missing key")
            # Treat the patientID as a number
            new_patient['patientID'] = int(new_patient['patientID'])
            # Treat the patientID as a number
            new_patient['roomID'] = int(new_patient['roomID'])
            # Check that both the name and the surname contain alphabetic chars only
            if not new_patient['name'].isalpha() or not new_patient['surname'].isalpha():
                raise ValueError("Patient Name/Surname is not alphabetic")
            # Treat the age as a number
            new_patient['age'] = int(new_patient['age'])

            # If the Patient is already present, abort the operation; otherwise, insert it in the Patient Catalog
            request = requests.post(self.__config_settings['host']+"/add-patient",data =json.dumps(new_patient))
            nattempts = 1
            while nattempts < 5 and str(request.status_code).startswith('5'):
                request = requests.post(self.__config_settings['host']+"/add-patient",data =json.dumps(new_patient))
                nattempts += 1
            if nattempts == 5 and str(request.status_code).startswith('5'):
                raise ServerNotFoundError
            if request.status_code == 400 :
                raise DuplicatePatientError
            if request.status_code == 406 :
                raise RoomNotFoundError
            else:
                update.message.reply_text("Patient added successfully!")

        except ValueError as e:
            update.message.reply_text(
                "Sorry, this Patient description is invalid.\n"
                "Please, use the following syntax:\n"
                "patientID - <insert_patientID>\n" 
                "roomID - <insert_roomID>\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                "age - <insert_age>\n"
                "description - <insert_description>")
            print(e)
            return SmartNursingBot.ADD_PATIENT
        except DuplicatePatientError as e:
            update.message.reply_text("This patient is already present! Retry")
            print(e)
            return SmartNursingBot.ADD_PATIENT
        except RoomNotFoundError as e:
            update.message.reply_text("Room not found! Retry")
            print(e)
            return SmartNursingBot.ADD_PATIENT
        except ServerNotFoundError as e:
            update.message.reply_text("Host unreachable. Abort")
            print(e)
            return SmartNursingBot.ADD_PATIENT
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
            return SmartNursingBot.EDIT_PATIENT_1
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __search_patient(self, update: Update, context: CallbackContext):
        try:
            # Understand which is the current command
            curr_command = context.chat_data['command']
            # Define a Patient from the User Data
            req_patient = SmartNursingBot.__parse_input(update.message.text)
            
            # Check if you have fetched the correct number of elements
            # Look for the Patient either by using the PatientID or their name and surname
            patient_present = False
            found_patients = [] 
            if len(req_patient) == 1: # Case in which the User provides the PatientID
                #if 'patientID' not in req_patient:
                #    raise ValueError("Missing key")
                req_patientID = int(req_patient['patientID'])
                nattempts = 1
                r = requests.get(self.__config_settings['host']+"/patient/"+str(req_patientID))
                while nattempts < 5 and r.status_code != requests.codes.ok : 
                    nattempts += 1
                    r = requests.get(self.__config_settings['host']+"/patient/"+str(req_patientID))

                if r.status_code == requests.codes.ok:
                    patient_present = True
                    found_patients.append(r.json())
                          
            # Case in which the User provides the Name and Surname of the patient
            elif len(req_patient) == 2:
                #if 'name' not in req_patient or 'surname' not in req_patient:
                #    raise Exception("Missing key")
                # Check that both the name and the surname contain alphabetic chars only
                if not req_patient['name'].isalpha() or not req_patient['surname'].isalpha():
                    raise ValueError("Patient Name/Surname is not alphabetic")
                # Try to contact the Server up to 5 times to retrieve the Patient Catalog
                nattempts = 1
                request = requests.get(self.__config_settings['host']+"/patients")
                while nattempts < 5 and request.status_code != requests.codes.ok:
                    nattempts += 1
                    request = requests.get(self.__config_settings['host']+"/patients")
                if nattempts == 5 and request.status_code != requests.codes.ok:
                    raise ServerNotFoundError
                patient_catalog = request.json()
                for patient in patient_catalog:
                    if patient['name'] == req_patient['name'] and patient['surname'] == req_patient['surname']:
                        patient_present = True
                        found_patients.append(patient)
            else:
                raise ValueError("Incorrect number of parameters")
                # If the Patient is not present, abort the operation; otherwise, display its data and ask for a new Patient description
            if patient_present:
                if len(found_patients) == 1:
                    found_patient = found_patients.pop()
                    # Store this infomation for when the new Patient description will be provided and the current one will be discarded
                    if curr_command == 'delete_patient':
                        context.chat_data['patientID_to_delete'] = found_patient['patientID']
                    elif curr_command == 'edit_patient':
                        context.chat_data['patientID_to_edit'] = found_patient['patientID']
                    msg = ("Patient found:\n" + "-"*40 + "\n" +
                        "patientID - {patientID}\n"   .format(patientID=      found_patient['patientID']) +
                        "roomID - {roomID}\n"         .format(roomID=         found_patient['roomID']) +
                        "name - {patientName}\n"      .format(patientName=    found_patient['name']) +
                        "surname - {patientSurname}\n".format(patientSurname= found_patient['surname']) + 
                        "age - {patientAge}\n"        .format(patientAge=     found_patient['age']) +
                        "description - {patientDescription}\n".format(patientDescription=found_patient['description']))
                    if curr_command == 'delete_patient':
                        msg += "-"*40 + "\n"
                        msg += "Are you sure you want to delete them? [Y/N]"
                    elif curr_command == 'edit_patient':
                        msg += "-"*40 + "\n"
                        msg += "Redefine the Patient using the same format without patientID"
                    update.message.reply_text(msg) 
                else:
                    msg = "Multiple Patients found!\n"
                    for found_patient in sorted(found_patients, key=lambda patient: patient['patientID']):
                        msg += "-"*40 + "\n" + \
                            "patientID - {patientID}\n".format(patientID=found_patient['patientID']) + \
                            "roomID - {roomID}\n".format(roomID=found_patient['roomID']) + \
                            "name - {patientName}\n".format(patientName=found_patient['name']) + \
                            "surname - {patientSurname}\n".format(patientSurname=found_patient['surname']) + \
                            "age - {patientAge}\n".format(patientAge=found_patient['age']) + \
                            "description - {patientDescription}\n".format(patientDescription=found_patient['description'])
                    if curr_command == 'delete_patient' or curr_command == 'edit_patient':
                        msg += "-"*40 + "\n"
                        msg += "Choose the patient by using their ID with the following format:\n" "patientID - <insert_patientID>" 
                    update.message.reply_text(msg)
                    if curr_command == 'delete_patient':
                        return SmartNursingBot.DELETE_PATIENT_1
                    elif curr_command == 'edit_patient':
                        return SmartNursingBot.EDIT_PATIENT_1             
            else:
                raise PatientNotFoundError

        except json.JSONDecodeError as e:
            update.message.reply_text(
                "Invalid answer from the Host. Abort."
            )
            print(e)  
            return ConversationHandler.END

        except (ValueError, KeyError) as e:
            update.message.reply_text(
                "Something went wrong. Please use the following format:\n"
                "patientID - <insert_patientID>\n" 
                "OR\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n")
            if curr_command == 'delete_patient':
                return SmartNursingBot.DELETE_PATIENT_1
            elif curr_command == 'edit_patient':
                return SmartNursingBot.EDIT_PATIENT_1 
            elif curr_command == 'search_patient':
                return SmartNursingBot.SEARCH_PATIENT

        except PatientNotFoundError as e:
            update.message.reply_text("Patient not found! Retry")
            print(e)
            if curr_command == 'delete_patient':
                return SmartNursingBot.DELETE_PATIENT_1
            elif curr_command == 'edit_patient':
                return SmartNursingBot.EDIT_PATIENT_1 
            elif curr_command == 'search_patient':
                return SmartNursingBot.SEARCH_PATIENT

        if curr_command == 'delete_patient':
            return SmartNursingBot.DELETE_PATIENT_2
        elif curr_command == 'edit_patient':
            return SmartNursingBot.EDIT_PATIENT_2
        return ConversationHandler.END #default bhv (also expected behavior for search_patient)

    def __edit_patient_update(self, update: Update, context: CallbackContext):
        try:
            edited_patient = SmartNursingBot.__parse_input(update.message.text)
            #print(edited_patient)
            # Check if you have fetched the correct number of elements
            if len(edited_patient) != 5:
                raise ValueError("Incorrect number of elements")
            # Check if all the excepted keys are present
            #if 'name' not in edited_patient or 'surname' not in edited_patient or \
            #    'age' not in edited_patient or 'description' not in edited_patient:
            #    raise Exception("Missing key")
            # Check that both the name and the surname contain alphabetic chars only
            if not edited_patient['name'].isalpha() or not edited_patient['surname'].isalpha():
                raise ValueError("Patient Name/Surname is not alphabetic")
            # Treat the age as a number
            edited_patient['age'] = int(edited_patient['age'])

            # Insert the RoomID in the edited Patient
            edited_patient['roomID'] = int(edited_patient['roomID'])

            # Insert the PatientID in the edited Patient
            edited_patient['patientID'] = context.chat_data['patientID_to_edit']

            # Take the Patient Catalog             
            nattempts = 1
            request = requests.put(self.__config_settings['host']+"/update-patient", data = json.dumps(edited_patient))
            while nattempts < 5 and str(request.status_code).startswith('5'):
                nattempts += 1 
                request = requests.put(self.__config_settings['host']+"/update-patient", data = json.dumps(edited_patient))
            if nattempts == 5 and str(request.status_code).startswith('5'):
                raise ServerNotFoundError
            elif request.status_code == 406:
                raise RoomNotFoundError
            else :
                update.message.reply_text("Patient updated successfully!")

        except (ValueError, KeyError) as e:
            update.message.reply_text(
                "Sorry, this Patient description is invalid.\n"
                "Please, use the following format:\n"
                "roomID - <insert_roomID>\n"
                "name - <insert_name>\n"
                "surname - <insert_surname>\n"
                "age - <insert_age>\n"
                "description - <insert_description>\n")
            # Retry until success
            return SmartNursingBot.EDIT_PATIENT_2
        
        except ServerNotFoundError:
            update.message.reply_text("Host unreachable. Abort")
            print(e)
            # Abort the command, it is not the user's fault
            return ConversationHandler.END
        
        except RoomNotFoundError:
            update.message.reply_text("Room not found! Retry")
            print(e)
            return SmartNursingBot.EDIT_PATIENT_2
 
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
            return SmartNursingBot.DELETE_PATIENT_1
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __delete_patient_update(self, update: Update, context: CallbackContext):
        try:
            text = update.message.text
            # Delete Patient
            if text == 'Y' or text == 'y':
                delete_patientID = context.chat_data['patientID_to_delete']
                nattempts = 1
                request = requests.delete(self.__config_settings['host']+"/delete-patient/"+str(delete_patientID))
                while nattempts < 5 and str(request.status_code).startswith('5') :
                    nattempts += 1
                    request = requests.delete(self.__config_settings['host']+"/delete-patient/"+str(delete_patientID))
                if request.status_code == 404:
                    raise PatientNotFoundError
                if nattempts == 5 and request.status_code != requests.codes.ok:
                    raise ServerNotFoundError
                update.message.reply_text("Patient removed successfully!")  
            # Do not Delete Patient
            elif text == 'N' or text == 'n':
                update.message.reply_text("Patient not deleted.\nAbort.")
            else:
                raise ValueError("Undefined Answer")

        except PatientNotFoundError as e:
            update.message.reply_text("Patient not deleted correctly! If you want to retry, relaunch the command.")
            print(e)
            return ConversationHandler.END

        except ServerNotFoundError as e:
            update.message.reply_text("Host unreachable. Abort.")
            print(e)
            # Abort the command, it is not the user's fault
            return ConversationHandler.END

        except ValueError as e:
            update.message.reply_text("Sorry, Reply with [Y/N]")
            print(e)
            # Retry until success
            return SmartNursingBot.DELETE_PATIENT_2
 
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
            return SmartNursingBot.SEARCH_PATIENT
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __show_patients(self, update: Update, context: CallbackContext):
        
        try:
            userID = update.message.from_user.id
            if self.__check_authZ_authN(update, 'show_patients', userID):
                context.chat_data['command'] = 'show_patients'
                nattempts = 1
                request = requests.get(self.__config_settings['host']+"/patients")
                while nattempts < 5 and request.status_code != requests.codes.ok :
                    nattempts += 1
                    request = requests.get(self.__config_settings['host']+"/patients")
                if nattempts == 5 and request.status_code != requests.codes.ok:
                    raise ServerNotFoundError
                patient_catalog = request.json()
                if len(patient_catalog) == 0:
                    msg = "No patient found"
                else:
                    msg = "Currently registered patients:\n"
                    for found_patient in sorted(patient_catalog, key=lambda p: p['patientID']):
                        msg +=  "-"*40 + "\n" + \
                                "patientID - {patientID}\n".format(patientID=found_patient['patientID']) + \
                                "roomID - {roomID}\n".format(roomID=found_patient['roomID']) + \
                                "name - {patientName}\n".format(patientName=found_patient['name']) + \
                                "surname - {patientSurname}\n".format(patientSurname=found_patient['surname']) + \
                                "age - {patientAge}\n".format(patientAge=found_patient['age']) + \
                                "description - {patientDescription}\n".format(patientDescription=found_patient['description']) 
                update.message.reply_text(msg)
            else:
                update.message.reply_text("Sorry, you cannot interact with the Bot!")
        except ServerNotFoundError as e:
            update.message.reply_text("Host unreachable. Abort.")
            print(e)
        except json.JSONDecodeError as e:
            update.message.reply_text("Invalid answer from the Host. Abort.")
            print(e)  

 
    def __set_room_temperature_entry(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'get_room_temperature', userID):
            update.message.reply_text(
                "To set the temperature of a room, use the following format:\n"
                "roomID - <insert_roomNumber>\n"
                "temp - <insert_temperature>\n"
                "isCommon - <True/False>"
                )
            context.chat_data['command'] = 'set_room_temperature'
            return SmartNursingBot.SET_ROOM_TEMPERATURE
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __set_room_temperature_update(self, update: Update, context: CallbackContext):
        
        try:
            room = SmartNursingBot.__parse_input(update.message.text)
            # Check if you have fetched the correct number of elements
            if len(room) != 3:
                raise ValueError("Incorrect number of elements")
            # Check if all the excepted keys are present
            #if 'roomID' not in room and 'temp' not in room:
            #    raise Exception("Missing key")
            # Treat the Room Number as an integer
            roomID = int(room['roomID'])
            # Treat the Room Temperature as an integer
            roomTemp = int(room['temp'])
            # Treat the fact that the Room is common as a boolean
            isCommon = room['isCommon'] == 'True'
            if isCommon:
                uri = "common-room"
            else:
                uri = "room"
            request = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
            nattempts = 1
            if nattempts < 5 and str(request.status_code).startswith('5'):
                request = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
                nattempts += 1
            
            if request.status_code == requests.codes.ok:
                # Set the Room info
                room = request.json()
                room['desired-temperature'] = roomTemp

                # Update the Room
                nattempts = 1
                request = requests.put(self.__config_settings['host']+"/update-"+uri+"/",data=json.dumps(room))
                while nattempts < 5 and str(request.status_code).startswith('5'):
                    nattempts += 1
                    request = requests.put(self.__config_settings['host']+"/update-"+uri+"/",data=json.dumps(room))
                if request.status_code == requests.codes.ok:
                    update.message.reply_text(
                        "Room Temperature for Room " + str(roomID) + ": updated!"
                    )
                elif nattempts == 5 and str(request.status_code).startswith('5'):
                    raise ServerNotFoundError
                elif request.status_code != requests.codes.ok:
                    raise RoomNotFoundError
            
            elif nattempts == 5 and str(request.status_code).startswith('5'):
                raise ServerNotFoundError

            elif request.status_code != requests.codes.ok:
                raise RoomNotFoundError

        except (ValueError, KeyError) as e:
            update.message.reply_text(
                "Something went wrong. "
                "Please, use the following format:\n"
                "roomID - <insert_roomNumber>\n"
                "temp - <insert_temperature>\n"
                "isCommon - <True/False>")
            print(e)
            # Retry until success
            return SmartNursingBot.SET_ROOM_TEMPERATURE
        
        except ServerNotFoundError as e:
            update.message.reply_text("Host unreachable. Abort")
            print(e)
            return ConversationHandler.END

        except RoomNotFoundError as e:
            update.message.reply_text("Room not found. Abort")
            print(e)
            return ConversationHandler.END

        return ConversationHandler.END

    def __get_room_temperature_entry(self, update: Update, context: CallbackContext):
        userID = update.message.from_user.id
        if self.__check_authZ_authN(update, 'get_room_temperature', userID):
            update.message.reply_text(
                "To read the temperature of a room, insert its number using the following format:\n"
                "roomID - <insert_roomID>\n"
                "isCommon - <True/False>"
                )
            context.chat_data['command'] = 'get_room_temperature'
            return SmartNursingBot.GET_ROOM_TEMPERATURE
        else:
            update.message.reply_text("Sorry, you cannot interact with the Bot!")
            return ConversationHandler.END

    def __get_room_temperature_update(self, update: Update, context: CallbackContext):
        try:
            room = SmartNursingBot.__parse_input(update.message.text)
            # Check if you have fetched the correct number of elements
            if len(room) != 2:
                raise ValueError("Incorrect number of elements")
            # Check if all the excepted keys are present
            #if 'roomID' not in room:
            #    raise Exception("Missing key")
            # Treat the Room Number as an integer
            roomID = int(room['roomID'])
            # Treat the fact that the Room is common as a boolean
            isCommon = room['isCommon'] == 'True'
            if isCommon:
                uri = "common-room"
            else:
                uri = "room"

            # Get the Room info 
            nattempts = 1
            request = requests.get(self.__config_settings['host']+"/"+uri+"-temperature/" + str(roomID))
            while nattempts < 5 and str(request.status_code).startswith('5'):
                nattempts += 1
                request = requests.get(self.__config_settings['host']+"/"+uri+"-temperature/" + str(roomID))
            if nattempts == 5 and str(request.status_code).startswith('5'):
                raise ServerNotFoundError
            if request.status_code == 404:
                raise RoomNotFoundError
            fetched_room = request.json()
            fetched_room_temp = int(fetched_room['desired-temperature'])
            if isCommon:
                update.message.reply_text(
                    "Temperature for Common Room " + str(roomID) + ": " + str(fetched_room_temp) + "°C"
                )
            else:
                update.message.reply_text(
                    "Temperature for Room " + str(roomID) + ": " + str(fetched_room_temp) + "°C"
                )

        except json.JSONDecodeError as e:
            update.message.reply_text("Invalid answer from the Host. Abort.")
            print(e)
            return ConversationHandler.END

        except (ValueError, KeyError) as e:
            update.message.reply_text(
                "Something went wrong. "
                "Please, use the following format:\n"
                "roomID - <insert_roomID>\n"
                "isCommon - <True/False>")
            print(e)
            # Retry until success
            return SmartNursingBot.GET_ROOM_TEMPERATURE

        except RoomNotFoundError as e:
            update.message.reply_text("Room not found! Abort")
            print(e)
            return ConversationHandler.END

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
                    raise ShiftStartedError

            else:
                update.message.reply_text("Sorry, you cannot interact with the Bot!")

        except ShiftStartedError as e:
            update.message.reply_text("You have already started to work!")
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
                    raise ShiftEndedError
                    
            else:
                update.message.reply_text("Sorry, you cannot interact with the Bot!")

        except ShiftEndedError as e:
            update.message.reply_text("You have already finished to work!")
            print(e)

    def __cancel(self, update: Update, context: CallbackContext):
        update.message.reply_text("Command aborted!")
        return ConversationHandler.END

    def updateService(self) :
        while True :
            sleep(int(self.__config_settings['updateTimeInSecond']))
            nattempts = 1
            r = requests.put(self.__config_settings['host'] + "/update-service",data = json.dumps({
            'serviceID' : int(self.__config_settings['serviceID']),
            'name' : self.__config_settings['name']
            }))
            while nattempts < 5 and r.status_code != requests.codes.ok:
                r = requests.put(self.__config_settings['host'] + "/update-service",data = json.dumps({
                'serviceID' : int(self.__config_settings['serviceID']),
                'name' : self.__config_settings['name']
                }))

if __name__ == '__main__':
    bot = SmartNursingBot()
    bot.launch()
    bot.updateService()
