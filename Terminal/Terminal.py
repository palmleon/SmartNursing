import requests
import json
import time
from threading import Thread
from enum import Enum

class CommandType(Enum):
    ROOM = 0
    USER_TELEGRAM = 1 

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

        elif command_type == CommandType.USER_TELEGRAM:
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
        print("Welcome to the SmartClinic Terminal!\n"
          "You can use this terminal to manage rooms and users!")
        print("-"*40)

        while(True): # The system should be shut down if you do not want to use it anymore
            
            # Launch menu 
            try:
                print("What do you want to manage?\n"
                    "room: to manage rooms\n"
                    "users: to manage users")
                print("-"*40)
                command_type = CommandType[input().upper()]
                print("-"*40)
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

    #########################################
    # Add a Room
    #########################################
    def __room_add(self):
        
        try:
            
            end = False

            while not end:

                # Insert Room Number
                roomID = int(input("Please insert the ID of the new room: "))
                isCommon_str = input("Is it common [Y/N]? ")

                 
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    newRoom = {
                        'roomID': roomID,
                        'desired-temperature': 20,
                        'isCommon': True
                    }

                    # Check if it is already taken
                    # If not, add it (TODO ADD THE ADD COMMON ROOM METHOD IN THE DEVICE REGISTRY SYSTEM)
                    r = requests.post(self.__config_settings['host']+"/add-common-room/", data = newRoom)
                    nattempts = 1

                    while nattempts < 5 and str(r.status_code).startswith('5'):
                        r = requests.post(self.__config_settings['host']+"/add-common-room/", data = newRoom)
                        nattempts += 1
                else:
                    newRoom = {
                        'roomID': roomID,
                        'desired-temperature': 20,
                        'patients': [],
                        'isCommon': False
                        #'sensors': []
                    }

                    # Check if it is already taken
                    # If not, add it                     
                    r = requests.post(self.__config_settings['host']+"/add-room/", data = newRoom)
                    nattempts = 1

                    while nattempts < 5 and str(r.status_code).startswith('5'):
                        r = requests.post(self.__config_settings['host']+"/add-room/", data = newRoom)
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
            print("Input not recognized! Retry.")

    #########################################
    # Search a Room
    #########################################
    def __room_search(self):

        try:

            while not end:
                # Insert Room Number
                roomID = int(input("Please insert the ID of room to search: "))
                isCommon_str = input("Is it common [Y/N]? ")

                # Check if it exists #TODO REST METHODS TO BE DEFINED!
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    r = requests.get(self.__config_settings['host']+"/common-room/"+str(roomID))
                else:
                    r = requests.get(self.__config_settings['host']+"/room/"+str(roomID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    if isCommon_str == 'Y' or isCommon_str == 'y':
                        r = requests.get(self.__config_settings['host']+"/common-room/"+str(roomID))
                    else:
                        r = requests.get(self.__config_settings['host']+"/room/"+str(roomID))
                    nattempts += 1 
                
                # If so, show it and all its data
                if r.status_code == requests.codes.ok:
                    print("Room found!")
                    json.dumps(r.json(), indent=4)
                    
                # Otherwise, retry or cancel the command
                else:
                    if nattempts == 5:
                        command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except ValueError:
            print("Input not recognized! Retry.")
        pass      

    #########################################
    # Edit a Room
    #########################################
    def __room_edit(self):
       
        try:

            while not end:
                # Insert Room Number
                roomID = int(input("Please insert the ID of the room to edit: "))
                isCommon_str = input("Is it common [Y/N]? ")

                # Check if it exists #TODO REST METHODS TO BE DEFINED!
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    r = requests.get(self.__config_settings['host']+"/common-room/"+str(roomID))
                else:
                    r = requests.get(self.__config_settings['host']+"/room/"+str(roomID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    if isCommon_str == 'Y' or isCommon_str == 'y':
                        r = requests.get(self.__config_settings['host']+"/common-room/"+str(roomID))
                    else:
                        r = requests.get(self.__config_settings['host']+"/room/"+str(roomID))
                    nattempts += 1 
                
                # If so, show it and all its data
                if r.status_code == requests.codes.ok:
                    print("Room found!")
                    room = r.json()
                    json.dumps(room, indent=4)

                    # Ask for the new room number
                    newRoomID = int(input("Please insert the new ID of the room to edit: "))

                    roomUpdated = {
                        'roomID_old' : roomID,
                        'roomID_new' : newRoomID
                    }
                    
                    # UPDATE THE ROOM ID TODO REST METHOD TO BE DEFINED
                    nattempts = 1
                    r = requests.put(self.__config_settings['host']+"/update-room-id", data=roomUpdated)

                    while nattempts < 5 and str(r.status_code).startswith('5'):
                        nattempts += 1
                        if isCommon_str == 'Y' or isCommon_str == 'y':
                            r = requests.put(self.__config_settings['host']+"/update-common-room-id", data=roomUpdated)
                        else:
                            r = requests.put(self.__config_settings['host']+"/update-room-id", data=roomUpdated)

                    if r.status_code == requests.codes.ok:
                        print("Room updated successfully!")
                        end = True
                    else:
                        if nattempts == 5 and str(r.status_code).startswith('5'):
                            command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                        else:
                            command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                        if command == 'q':
                            end = True
                    
                # Otherwise, retry or cancel the command
                else:
                    if nattempts == 5:
                        command = input("Operation failed: Server not reachable! Retry [r] or quit [q]: ")
                    else:
                        command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except ValueError:
            print("Input not recognized! Retry.")     

    #########################################
    # Show all Rooms
    #########################################
    def __room_show(self):
        # Show all rooms, the patients inside and the sensors
        r = requests.get(self.__config_settings['host']+"room-list")
        nattempts = 1

        while nattempts < 5 and str(r.status_code).startswith('5'):
            r = requests.get(self.__config_settings['host']+"room-list")
            nattempts += 1

        if r.status_code == requests.codes.ok:
            print("Registered Rooms and their content:")
            json.dumps(r.json(), indent=4)

        else:
            if nattempts == 5:
                print("Operation failed: Server not reachable!")
            else:
                print("Operation failed: Unknown error!")

        # Show all common rooms
        r = requests.get(self.__config_settings['host']+"common-room-list")
        nattempts = 1

        while nattempts < 5 and str(r.status_code).startswith('5'):
            r = requests.get(self.__config_settings['host']+"common-room-list")
            nattempts += 1

        if r.status_code == requests.codes.ok:
            print("Registered Common Rooms and their content:")
            json.dumps(r.json(), indent=4)

        else:
            if nattempts == 5:
                print("Operation failed: Server not reachable!")
            else:
                print("Operation failed: Unknown error!")        
            


    #########################################
    # Delete a Room
    #########################################
    def __room_delete(self):
    
        try:

            end = False

            while not end:

                # Insert Room Number
                roomID = int(input("Please insert the ID of the room to delete: "))
                isCommon_str = input("Is it common [Y/N]? ")
                
                # Check if it exists #TODO REST METHOD TO BE DEFINED!
                if isCommon_str == 'Y' or isCommon_str == 'y':
                    r = requests.get(self.__config_settings['host']+"/common-room/"+str(roomID))
                else:
                    r = requests.get(self.__config_settings['host']+"/room/"+str(roomID))
                nattempts = 1
                
                while nattempts < 5 and str(r.status_code).startswith('5'):
                    if isCommon_str == 'Y' or isCommon_str == 'y':
                        r = requests.get(self.__config_settings['host']+"/common-room/"+str(roomID))
                    else:
                        r = requests.get(self.__config_settings['host']+"/room/"+str(roomID))
                    nattempts += 1 
                
                # If so, show it and all its data
                if r.status_code == requests.codes.ok:
                    print("Room found!")
                    room = r.json()
                    json.dumps(room, indent=4)

                    # If so, and if there is no patient inside, ask for confirmation
                    if room['isCommon'] or len(room['patients']) == 0:
                        confirm_reply = input("Are you sure you want to delete this user [Y/N]? ")
                        
                        # Delete or not depending on confirmation reply (TODO IMPLEMENT DELETE COMMON ROOM)
                        if confirm_reply == 'Y' or confirm_reply == 'y':

                            if isCommon_str == 'Y' or isCommon_str == 'y':
                                r = requests.delete(self.__config_settings['host']+"/delete-common-room/"+str(userID))
                            else:
                                r = requests.delete(self.__config_settings['host']+"/delete-room/"+str(userID))
                            nattempts = 1

                            while nattempts < 5 and str(r.status_code).startswith('5'):
                                if isCommon_str == 'Y' or isCommon_str == 'y':
                                    r = requests.delete(self.__config_settings['host']+"/delete-common-room/"+str(userID))
                                else:
                                    r = requests.delete(self.__config_settings['host']+"/delete-room/"+str(userID))                            
                                nattempts += 1

                            if r.status_code == requests.codes.ok:
                                print("User deleted!")
                                end = True
                            else:
                                if nattempts == 5:
                                    command = input(("Operation failed: Server not reachable! Retry [r] or quit [q]: "))
                                else:
                                    command = input("Operation failed: Room not found! Retry [r] or quit [q]: ")
                                if command == 'q':
                                    end = True

                        else:
                            print("Operation aborted.")
                            end = True

                    # Otherwise, if the room has patients inside, cancel the command
                    else:
                        print("You cannot delete this Room: there are patients inside!")
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
            print("Input not recognized! Retry.")

    #########################################
    # Add a User to the Telegram ID List
    #########################################
    def __user_telegram_add(self):
         
        try:

            end = False

            while not end:

                # Retrieve UserID and Role
                userID = int(input("Please insert the UserID to add: "))
                role = Role[input("Please insert their role [Doctor, Nurse, SuperUser]: ").upper()]

                # Check if the UserID is already present in the Telegram ID List
                nattempts = 1
                r = requests.post(self.__config_settings['host']+"/add-telegram-user-id/", data = json.dumps({
                    'user-id': userID,
                    'role' : role
                }))
                while nattempts < 5 and str(r.status_code).startswith('5'):
                    nattempts += 1
                    r = requests.post(self.__config_settings['host']+"/add-telegram-user-id/", data = json.dumps({
                    'user-id': userID,
                    'role' : role
                }))
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
            print("Input not recognized! Retry.")

    #########################################
    # Search a User in the Telegram ID List
    #########################################
    def __user_telegram_search(self):

        try:

            end = False

            while not end:

                # Retrieve UserID
                userID = int(input("Please insert the UserID to search: "))
                
                # Look for the UserID in the Telegram ID List TODO PATH TO BE DEFINED YET!
                r = requests.get(self.__config_settings['host'] + "/get-telegram-user-id/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/get-telegram-user-id/" + str(userID))
                    nattempts += 1

                # If present, show it
                if r.status_code == requests.codes.ok:
                    user = r.json()
                    print("User found!")
                    print("UserID: {userID}\n Role: {role}".format(userID=user['user-id'], role=user['role']))
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
            print("Input not recognized! Retry.")

    #########################################
    # Edit a User of the Telegram ID List
    #########################################
    def __user_telegram_edit(self):

        try:

            end = False

            while not end:

                # Retrieve UserID
                userID = int(input("Please insert the UserID to edit: "))
                
                # Look for the UserID in the Telegram ID List TODO PATH TO BE DEFINED YET!
                r = requests.get(self.__config_settings['host'] + "/telegram-user-id/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/telegram-user-id/" + str(userID))
                    nattempts += 1

                # If present, ask for the new role
                if r.status_code == requests.codes.ok:

                    # Retrieve the new Role and check that it is meaningful
                    role = Role[input("Set the new role: ").upper()]

                    # Update the UserID in the Telegram ID List
                    nattempts = 1
                    r = requests.put(self.__config_settings['host']+"/update-telegram-user-id/", data = json.dumps({
                            'user-id': userID,
                            'role' : role
                        }))
                    while nattempts < 5 and str(r.status.code).startswith('5'):
                        nattempts += 1
                        r = requests.put(self.__config_settings['host']+"/update-telegram-user-id/", data = json.dumps({
                            'user-id': userID,
                            'role' : role
                        }))

                    if r.status_code == requests.status_codes.ok:
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
            print("Input not recognized! Retry.")

    #########################################
    # Show all Users from the Telegram ID List
    #########################################
    def __user_telegram_show(self):
        
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
        for user in user_id_list:
            print("UserID: {userID}, Role: {role}".format(userID=user['user-id'], role=user['role']))
        

    #########################################
    # Delete a User from the Telegram ID List
    #########################################
    def __user_telegram_delete(self):

        try:

            end = False

            while not end:

                # Retrieve UserID
                userID = int(input("Please insert the UserID to delete: "))
                
                # Look for the UserID in the Telegram ID List TODO PATH TO BE DEFINED YET!
                r = requests.get(self.__config_settings['host'] + "/telegram-user-id/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/telegram-user-id/" + str(userID))
                    nattempts += 1

                # If present, ask for confirmation
                if r.status_code == requests.codes.ok:

                    end = True
                    user = r.json()
                    print("User found!")
                    print("UserID: {userID}, Role: {role}".format(userID=user['user-id'], role=user['role']))
                    confirm_reply = input("Are you sure you want to delete this user [Y/N]? ")
                    
                    # Delete or not depending on confirmation reply
                    if confirm_reply == 'Y' or confirm_reply == 'y':

                        r = requests.delete(self.__config_settings['host']+"/delete-telegram-user-id/"+str(userID))
                        nattempts = 1

                        while nattempts < 5 and str(r.status_code).startswith('5'):
                            r = requests.delete(self.__config_settings['host']+"/delete-telegram-user-id/"+str(userID))
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
                        command = input(("Operation failed: Server not reachable! Retry [r] or quit [q]: "))
                    else:
                        command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except (ValueError, KeyError):
            print("Input not recognized! Retry.")

    def __updateService(self) :

        while True :

            time.sleep(100)

            nattempts = 1
            r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__config_settings['serviceID'],
                 "name" : self.__config_settings['name']}))

            while nattempts < 5 and str(r.status_code).startswith('5'):
                nattempts += 1
                r = requests.put(self.__register+"/update-service",data = json.dumps({"serviceID" : self.__config_settings['serviceID'],
                 "name" : self.__config_settings['name']}))

    ###################################################################################################
    # During initialization, only the configuration file is set, and the updating thread is launched
    ###################################################################################################
    def __init__(self):
        
        # Load settings
        config_file = open('config.json')
        self.__config_settings = json.load(config_file)
        config_file.close()

        # Launch thread for service update
        thread = Thread(target=self.__updateService, args=(), daemon=False)
        thread.start()

if __name__ == '__main__':

    terminal = Terminal()

    # Launch Service
    terminal.launch()
    

