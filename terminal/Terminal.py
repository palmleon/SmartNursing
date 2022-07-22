import requests
import json
import time
import signal
from threading import Thread
from enum import Enum
import time

class CommandType(Enum):
    ROOM = 0
    USER = 1 
    EXIT = 2

class Command(Enum):
    ADD = 0
    SEARCH = 1
    EDIT = 2
    SHOW = 3
    DELETE = 4

class Role(Enum):
    NURSE = "Nurse"
    DOCTOR = "Doctor"
    SUPERUSER = "SuperUser"


class Terminal(object):

    ##########################
    # Very simple dispatcher
    ##########################
    def __handle_command(self, command: Command, command_type: CommandType):
        """
            Very simple dispatcher that executes the command handler corresponding to the given command.

            Args:
                command: the input command
                command_type: the kind of command [ROOM/USER]
        """
        
        if command_type == CommandType.ROOM:

            # Add Room
            if command == Command.ADD:
                self.__room_add()
                pass

            # Search Room
            elif command == Command.SEARCH:
                self.__room_search()
                pass

            # Edit Room
            elif command == Command.EDIT:
                self.__room_edit()
                pass

            # Show Room
            elif command == Command.SHOW:
                self.__room_show()
                pass

            # Delete Room
            elif command == Command.DELETE:
                self.__room_delete()
                pass

        elif command_type == CommandType.USER:
            # Add User
            if command == Command.ADD:
               self.__user_telegram_add()

            # Search User
            elif command == Command.SEARCH:
                self.__user_telegram_search()

            # Edit User
            elif command == Command.EDIT:
                self.__user_telegram_edit()

            # Show User
            elif command == Command.SHOW:
                self.__user_telegram_show()

            # Delete User
            elif command == Command.DELETE:
                self.__user_telegram_delete()

    def launch(self):
        """
            Launch the Terminal as an endless loop where the menu is printed and then a command is read and processed.  
        """
        
        print("\nWelcome to the SmartNursing Terminal!\n"
          "You can use this terminal to manage rooms and users!")
        print("-"*40)

        while(True): # The system should be shut down with an EXIT command
            
            # Launch menu 
            try:
                print("What do you want to manage?\n"
                    "room: to manage rooms\n"
                    "user: to manage users\n"
                    "exit: to exit")
                print("-"*40)
                command_type = CommandType[input().upper()]
                print("-"*40, flush=True)
                if command_type == CommandType.ROOM:
                    print("Commands available:\n"
                        "add: add a room\n"
                        "search: search a room\n"
                        "edit: edit a room\n"
                        "show: show all the rooms\n"
                        "delete: remove a room")
                elif command_type == CommandType.USER:
                    print("Commands available:\n"
                        "add: add an user\n"
                        "search: search an user\n"
                        "edit: edit an user\n"
                        "show: show all the users\n"
                        "delete: remove an user")
                elif command_type == CommandType.EXIT:
                    print('Quitting (wait a few seconds)...',flush=True)
                    return
                print("-"*40)

                # Catch command
                command = Command[input().upper()]
                print("-"*40)

                # Handle command
                self.__handle_command(command, command_type)
                print("-"*40)

                # Repeat

            except KeyError:
                print("-"*40)
                print("Command not recognized! Retry.")
                print("-"*40)

    def stop(self):
        """
            Stop the Terminal
        """
        self.__running = False
        self.__thread.join()

    def __room_add(self):
        """
            Add a Room to the Room Catalog.
            The Room can be common or not. To define a new Room, a new RoomID should be provided.
            If it is already taken, the command fails and user can either retry or cancel the operation.
            Otherwise, a the new Room is added to the Room Catalog.
        """
        
        try:
            
            end = False

            while not end:

                # Insert Room Number
                roomID = int(input("Please insert the ID of the new room: "))
                isCommon_str = input("Is it common [Y/N]? ")
                print()

                newRoom = None
                 
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    newRoom = {
                        'roomID': roomID,
                        'desired-temperature': 20
                    }
                    uri = 'common-room'
                else:
                    newRoom = {
                        'roomID': roomID,
                        'desired-temperature': 20,
                        'patients': []
                        #'sensors': []
                    }
                    uri = 'room'

                # Check if it is already taken
                # If not, add it 
                r = requests.post(self.__config_settings['host']+"/add-"+uri, data=json.dumps(newRoom))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.post(self.__config_settings['host']+"/add-"+uri, data=json.dumps(newRoom))
                    nattempts += 1
                
                if r.status_code == requests.codes.ok:
                    print("Room added successfully!")
                    end = True
                else:
                    if nattempts == 5 and str(r.status_code).startswith('5'):
                        command = input("Operation failed: Server unreachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: Room already present! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

                # Otherwise, retry or cancel the command
        except ValueError:
            print("Input not recognized! Abort.")

    def __room_search(self):
        """
            Search a Room in the Room Catalog.
            Given a roomID, the Terminal looks for a corresponding room in the Room Catalog.
            If it exists, all Room data is displayed, otherwise the Terminal informs the User that it has not been found.
        """
        try:
            
            end = False
            while not end:
                # Insert Room Number
                roomID = int(input("Please insert the ID of room to search: "))
                isCommon_str = input("Is it common [Y/N]? ")
                print()

                # Check if it exists
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    uri = 'common-room'
                else:
                    uri = 'room'

                r = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
                nattempts = 1
                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
                    nattempts += 1 
                
                # If so, show it and all its data
                if r.status_code == requests.codes.ok:
                    print("ROOM FOUND!",end='')
                    room = r.json()
                    if isCommon_str == 'Y' or isCommon_str == 'y':
                        msg = "\nRoomID: {roomID}".format(roomID=room['roomID']) + \
                            "\nDesired Temperature: {temperature}°C".format(temperature=room['desired-temperature'])
                    else:
                        msg = "\nRoomID: {roomID}".format(roomID=room['roomID']) + \
                            "\nDesired Temperature: {temperature}°C".format(temperature=room['desired-temperature']) + \
                            "\nPatients: {"
                        for patient in room['patients']:
                            msg += "\n"
                            msg += "\tPatientID: {patientID}\n".format(patientID=patient['patientID'])
                            msg += "\tName: {name}\n".format(name=patient['name'])
                            msg += "\tSurname: {surname}\n".format(surname=patient['surname'])
                            msg += "\tAge: {age}\n".format(age=patient['age'])
                            msg += "\tDescription: {description}\n".format(description=patient['description'])
                        msg += "}"   
                    print(msg)
                    end = True
                    
                # Otherwise, retry or cancel the command
                else:
                    if nattempts == 5 and str(r.status_code).startswith('5'):
                        command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except ValueError:
            print("Input not recognized! Abort.")
        pass      

    def __room_edit(self):
        """
            Edit a Room in the Room Catalog, i.e. change its roomID.
            The Terminal asks for the roomID of the Room to edit; if it exists, the User can change its roomID.
            Otherwise, the Terminal informs the User that it has not been found.
        """
        try:

            end = False
            while not end:
                # Insert Room Number
                roomID = int(input("Please insert the ID of the room to edit: "))
                isCommon_str = input("Is it common [Y/N]? ")
                print()

                # Check if it exists
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    uri = 'common-room'
                else:
                    uri = 'room'
                
                r = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
                    nattempts += 1 
                
                # If so, show it and all its data
                if r.status_code == requests.codes.ok:
                    print("ROOM FOUND!",end='')
                    room = r.json()
                    if isCommon_str == 'Y' or isCommon_str == 'y':
                        msg = "\nRoomID: {roomID}".format(roomID=room['roomID']) + \
                            "\nDesired Temperature: {temperature}°C".format(temperature=room['desired-temperature'])
                    else:
                        msg = "\nRoomID: {roomID}".format(roomID=room['roomID']) + \
                            "\nDesired Temperature: {temperature}°C".format(temperature=room['desired-temperature']) + \
                            "\nPatients: {"
                        for patient in room['patients']:
                            msg += "\n"
                            msg += "\tPatientID: {patientID}\n".format(patientID=patient['patientID'])
                            msg += "\tName: {name}\n".format(name=patient['name'])
                            msg += "\tSurname: {surname}\n".format(surname=patient['surname'])
                            msg += "\tAge: {age}\n".format(age=patient['age'])
                            msg += "\tDescription: {description}\n".format(description=patient['description'])
                        msg += "}"   
                    print(msg)

                    # Ask for the new room number
                    newRoomID = int(input("Please insert the new ID of the room to edit: "))
                    
                    room['roomID_old'] = room['roomID']
                    room['roomID'] = newRoomID
                    
                    # Update the Room ID
                    nattempts = 1
                    r = requests.put(self.__config_settings['host']+"/update-"+uri, data=json.dumps(room))

                    while nattempts < 5 and str(r.status_code).startswith('5'):
                        nattempts += 1
                        r = requests.put(self.__config_settings['host']+"/update-"+uri, data=json.dumps(room))
                        
                    if r.status_code == requests.codes.ok:
                        print("Room updated successfully!")
                        end = True
                    else:
                        if nattempts == 5 and str(r.status_code).startswith('5'):
                            command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                        else:
                            command = input("Operation failed: Room already existing! Retry [r] or quit [q]: ")
                        if command == 'q':
                            end = True
                    
                # Otherwise, retry or cancel the command
                else:
                    if nattempts == 5 and str(r.status_code).startswith('5'):
                        command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except ValueError:
            print("Input not recognized! Abort.")     

    def __room_show(self):
        """
            Display all Rooms in the Room Catalog, with their data.
        """
        # Show all rooms, the patients inside and the sensors
        r = requests.get(self.__config_settings['host']+"/room-list")
        nattempts = 1
        
        while nattempts < 5 and str(r.status_code).startswith('5'):
            r = requests.get(self.__config_settings['host']+"/room-list")
            nattempts += 1

        if r.status_code == requests.codes.ok:
            print("Registered Rooms and their content:")
            print("*"*40)
            rooms = r.json()
            for room in sorted(rooms, key=lambda room: room['roomID']):
                msg = "RoomID: {roomID}\n".format(roomID=room['roomID']) + \
                        "Desired Temperature: {temperature}°C\n".format(temperature=room['desired-temperature']) + \
                        "Patients: {"
                for patient in room['patients']:
                    msg += "\n"
                    msg += "\tPatientID: {patientID}\n".format(patientID=patient['patientID'])
                    msg += "\tName: {name}\n".format(name=patient['name'])
                    msg += "\tSurname: {surname}\n".format(surname=patient['surname'])
                    msg += "\tAge: {age}\n".format(age=patient['age'])
                    msg += "\tDescription: {description}\n".format(description=patient['description'])
                msg += "}\n"    
                print(msg)

        else:
            if nattempts == 5 and str(r.status_code).startswith('5'):
                print("Operation failed: Server not reachable!")
            else:
                print("Operation failed: Unknown error!")

        # Show all common rooms
        r = requests.get(self.__config_settings['host']+"/common-room-list")
        nattempts = 1

        while nattempts < 5 and str(r.status_code).startswith('5'):
            r = requests.get(self.__config_settings['host']+"/common-room-list")
            nattempts += 1

        if r.status_code == requests.codes.ok:
            print("Registered Common Rooms and their content:")
            print("*"*40,end='')
            rooms = r.json()
            for room in rooms:
                msg = "\nRoomID: {roomID}".format(roomID=room['roomID']) + \
                        "\nDesired Temperature: {temperature}°C".format(temperature=room['desired-temperature'])
                print(msg)

        else:
            if nattempts == 5 and str(r.status_code).startswith('5'):
                print("Operation failed: Server not reachable!")
            else:
                print("Operation failed: Unknown error!")        
            
    def __room_delete(self):
        """
            Remove a Room from the Room Catalog.
            The Terminal asks for the roomID of the Room to be removed and if it is common.
            If present, it asks for confirmation and acts according to the reply.
            Otherwise, the Terminal informs the User that the Room does not exists.
        """
        try:

            end = False

            while not end:

                # Insert Room Number
                roomID = int(input("Please insert the ID of the room to delete: "))
                isCommon_str = input("Is it common [Y/N]? ")
                print()
                
                # Check if it exists
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    uri = 'common-room'
                else:
                    uri = 'room'

                r = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
                nattempts = 1
                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host']+"/"+uri+"/"+str(roomID))
                    nattempts += 1 
                
                # If so, show it and all its data
                if r.status_code == requests.codes.ok:
                    print("ROOM FOUND!",end='')
                    room = r.json()
                    if isCommon_str == 'Y' or isCommon_str == 'y':
                        msg = "\nRoomID: {roomID}".format(roomID=room['roomID']) + \
                            "\nDesired Temperature: {temperature}°C".format(temperature=room['desired-temperature'])
                    else:
                        msg = "\nRoomID: {roomID}".format(roomID=room['roomID']) + \
                            "\nDesired Temperature: {temperature}°C".format(temperature=room['desired-temperature']) + \
                            "\nPatients: {"
                        for patient in room['patients']:
                            msg += "\n"
                            msg += "\tPatientID: {patientID}\n".format(patientID=patient['patientID'])
                            msg += "\tName: {name}\n".format(name=patient['name'])
                            msg += "\tSurname: {surname}\n".format(surname=patient['surname'])
                            msg += "\tAge: {age}\n".format(age=patient['age'])
                            msg += "\tDescription: {description}\n".format(description=patient['description'])
                        msg += "}"   
                    print(msg)

                    # If so, and if there is no patient inside, ask for confirmation
                    if isCommon_str == 'Y' or isCommon_str == 'y' or len(room['patients']) == 0:
                        confirm_reply = input("Are you sure you want to delete this Room [Y/N]? ")
                        
                        # Delete or not depending on confirmation reply
                        if confirm_reply == 'Y' or confirm_reply == 'y':

                            r = requests.delete(self.__config_settings['host']+"/delete-"+uri+"/"+str(roomID))
                            nattempts = 1

                            while nattempts < 5 and str(r.status_code).startswith('5'):
                                r = requests.delete(self.__config_settings['host']+"/delete-"+uri+"/"+str(roomID))                          
                                nattempts += 1

                            if r.status_code == requests.codes.ok:
                                print("Room deleted!")
                                end = True
                            else:
                                if nattempts == 5 and str(r.status_code).startswith('5'):
                                    command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                                else:
                                    command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                                if command == 'q':
                                    end = True

                        else:
                            print("Operation aborted.")
                            end = True

                    # Otherwise, if the room has patients inside, cancel the command
                    else:
                        print("You cannot delete this Room: there are patients inside! Please, move them before removing the room and retry.")
                        end = True
                    
                # Otherwise, retry or cancel the command
                else:
                    if nattempts == 5:
                        command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except (ValueError, KeyError):
            print("Input not recognized! Abort.")

    def __user_telegram_add(self):
        """
            Add a new User to the list of authenticated Telegram Users.
            The Terminal asks for both the Telegram userID and the role [Nurse, Doctor, SuperUser] of the new User,
            then it proceeds to insert the new user in the list.
        """
        try:

            end = False

            while not end:

                # Retrieve UserID and Role
                userID = int(input("Please insert the UserID to add: "))
                role = Role[input("Please insert their role [Doctor, Nurse, SuperUser]: ").upper()].value

                newUser = {
                    'user-id': userID,
                    'role': role
                }

                # Check if the UserID is already present in the Telegram ID List
                nattempts = 1
                r = requests.post(self.__config_settings['host']+"/add-telegram-user/", data = json.dumps(newUser))
                while nattempts < 5 and str(r.status_code).startswith('5'):
                    nattempts += 1
                    r = requests.post(self.__config_settings['host']+"/add-telegram-user/", data = json.dumps(newUser))
                if r.status_code == requests.codes.ok:
                    print("User added successfully!")
                    end = True
                else:
                    if nattempts == 5:
                        command = input(("Operation failed: Server not reachable! Retry [r] or quit [q]: "))
                    else:
                        command = input("Operation failed: User already present! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except (ValueError, KeyError):
            print("Input not recognized! Abort.")

    def __user_telegram_search(self):
        """
            Look for a Telegram User using the userID to search them.
            The Terminal looks for the User and, if present, it shows all the User related data (i.e. userID and role).
            Otherwise, the Terminal informs that the User does not exist.        
        """
        try:

            end = False

            while not end:

                # Retrieve UserID
                userID = int(input("Please insert the UserID to search: "))
                print()
                
                # Look for the UserID in the Telegram ID List
                r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                    nattempts += 1

                # If present, show it
                if r.status_code == requests.codes.ok:
                    user = r.json()
                    print("USER FOUND!")
                    print("UserID: {userID},\t Role: {role}".format(userID=user['user-id'], role=user['role']))
                    end = True

                # Otherwise, notify that it does not exist
                else:
                    if nattempts == 5:
                        command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except (ValueError, KeyError):
            print("Input not recognized! Abort.")

    def __user_telegram_edit(self):
        """
            Edit a Telegram User, i.e. set their role.
            Given a userID, the Terminal checks if it is present and, if that is the case, it asks for the new user role.
            Finally, it updates the Telegram User list.
            If it is not present, the Terminal informs the User that the User is not present.
        """
        try:

            end = False

            while not end:

                # Retrieve UserID
                userID = int(input("Please insert the UserID to edit: "))
                print()
                
                # Look for the UserID in the Telegram ID List
                r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                    nattempts += 1

                # If present, ask for the new role
                if r.status_code == requests.codes.ok:

                    user = r.json()
                    print("USER FOUND!")
                    print("UserID: {userID},\t Role: {role}".format(userID=user['user-id'], role=user['role']))
                   
                    # Retrieve the new Role and check that it is meaningful
                    role = Role[input("Set the new role: ").upper()].value

                    # Update the UserID in the Telegram ID List
                    nattempts = 1
                    editedUser = {
                            'user-id': userID,
                            'role' : role
                        }

                    r = requests.put(self.__config_settings['host']+"/update-telegram-user/", data = json.dumps(editedUser))
                    while nattempts < 5 and str(r.status_code).startswith('5'):
                        nattempts += 1
                        r = requests.put(self.__config_settings['host']+"/update-telegram-user/", data = json.dumps(editedUser))

                    if r.status_code == requests.codes.ok:
                        print("User updated successfully!")
                        end = True
                    else:
                        if nattempts == 5:
                            command = input(("Operation failed: Server not reachable! Retry [r] or quit [q]: "))
                        else:
                            command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                        if command == 'q':
                            end = True

                # Otherwise, notify that it does not exist
                else:
                    if nattempts == 5:
                        command = input(("Operation failed: Server not reachable! Retry [r] or quit [q]: "))
                    else:
                        command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except (ValueError, KeyError):
            print("Input not recognized! Abort.")

    def __user_telegram_show(self):
        
        """
            Display all Telegram Users and their data
        """

        # Retrieve the Telegram ID List
        nattempts = 1
        request = requests.get(self.__config_settings['host']+ "/telegram-user-id-list")
        while nattempts < 5 and str(request.status_code).startswith('5'):
            nattempts += 1
            request = requests.get(self.__config_settings['host']+ "/telegram-user-id-list")

        if nattempts == 5 and request.status_code != requests.codes.ok:
            print("Operation failed! Server not reachable")
            return

        # Display it in a clear format
        print("Registered users and their roles:")
        user_id_list = request.json()
        for user in sorted(user_id_list, key=lambda user: user['user-id']):
            print("UserID: {userID}, Role: {role}".format(userID=user['user-id'], role=user['role']))
        

    def __user_telegram_delete(self):
        """
            Remove a User from the Telegram User List.
            The Terminal asks for the userID of the User to be removed and, if it is present, it asks for confirmation and
            acts according to the reply. If it is not present, the Terminal informs the User and asks either to reply or to cancel the command.
        """
        try:

            end = False

            while not end:

                # Retrieve UserID
                userID = int(input("Please insert the UserID to delete: "))
                print()
                
                # Look for the UserID in the Telegram ID List
                r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                    nattempts += 1

                # If present, ask for confirmation
                if r.status_code == requests.codes.ok:

                    end = True
                    user = r.json()
                    print("USER FOUND!")
                    print("UserID: {userID}, Role: {role}".format(userID=user['user-id'], role=user['role']))
                    confirm_reply = input("Are you sure you want to delete this user [Y/N]? ")
                    
                    # Delete or not depending on confirmation reply
                    if confirm_reply == 'Y' or confirm_reply == 'y':

                        r = requests.delete(self.__config_settings['host']+"/delete-telegram-user/"+str(userID))
                        nattempts = 1

                        while nattempts < 5 and str(r.status_code).startswith('5'):
                            r = requests.delete(self.__config_settings['host']+"/delete-telegram-user/"+str(userID))
                            nattempts += 1

                        if r.status_code == requests.codes.ok:
                            print("User deleted!")
                            end = True
                        else:
                            if nattempts == 5:
                                command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                            else:
                                command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                            if command == 'q':
                                end = True

                    else:
                        print("Operation aborted.")
                        end = True

                # Otherwise, notify that it does not exist
                else:
                    if nattempts == 5:
                        command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except (ValueError, KeyError):
            print("Input not recognized! Abort.")

    def __updateService(self) :
        """
            Notify the device service registry that the Terminal is up and running every 'updateTimeInSecond' seconds
        """

        while self.__running :

            wait_time = 0
            while wait_time < self.__config_settings['updateTimeInSeconds'] and self.__running:
                time.sleep(5)
                wait_time += 5

            if self.__running:
                nattempts = 1
                r = requests.put(self.__config_settings['host']+"/update-service",data = json.dumps({
                        "serviceID" : self.__config_settings['serviceID'],
                        "name" : self.__config_settings['name']
                    }))

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    nattempts += 1
                    r = requests.put(self.__config_settings['host']+"/update-service",data = json.dumps({
                        "serviceID" : self.__config_settings['serviceID'],
                        "name" : self.__config_settings['name']
                    }))

    ###################################################################################################
    # During initialization, only the configuration file is set, and the updating thread is launched
    ###################################################################################################
    def __init__(self):
        """
            Constructor where the configuration settings are loaded and the thread which updates the service in the device service registry is launched.
        """
        
        # Load settings
        config_file = open('./config.json')
        self.__config_settings = json.load(config_file)
        config_file.close()

        self.__running = True
        
        r=requests.post(self.__config_settings['host']+"/add-service",data=json.dumps({"serviceID" : self.__config_settings['serviceID'], "name" : self.__config_settings['name']}))
        while r.status_code != requests.codes.ok:
            r = requests.post(self.__config_settings['host'] + "/add-service",data = json.dumps({
            'serviceID' : self.__config_settings['serviceID'],
            'name' : self.__config_settings['name']
            }))
        
        # Launch thread for service update
        self.__thread = Thread(target=self.__updateService, args=(), daemon=False)
        self.__thread.start()
    
    
def alarm_handler(signum, frame):
    raise TimeoutError

def input_with_timeout(timeout):
    signal.signal(signal.SIGALRM, alarm_handler) # the lambda is only used to raise an Exception in case the timer expires
    signal.alarm(timeout) # produce SIGALRM in `timeout` seconds 
    reply = None
    try:
        reply = input("\rPress enter to start: ")
    except TimeoutError:
        pass
    finally:
        signal.alarm(0) # cancel alarm
        if reply != None:
            return False
        else:
            return True

if __name__ == '__main__':

    terminal = Terminal()

    # Timed input to start the terminal
    timer_active = True
    while timer_active:
        timer_active = input_with_timeout(5)

    # Launch Service
    terminal.launch()
    terminal.stop()
