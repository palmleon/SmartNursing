from subprocess import TimeoutExpired
import requests
import json
import time
import signal
from threading import Thread
from enum import Enum

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

        print("\nWelcome to the SmartClinic Terminal!\n"
          "You can use this terminal to manage rooms and users!")
        print("-"*40)

        while(True): # The system should be shut down if you do not want to use it anymore
            
            # Launch menu 
            try:
                print("What do you want to manage?\n"
                    "room: to manage rooms\n"
                    "user: to manage users\n"
                    "exit: to exit")
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
                elif command_type == CommandType.EXIT:
                    return
                #elif command_type == CommandType.EXIT:
                #    return
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
        self.__running = False
        self.__thread.join()

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
                r = requests.post(self.__config_settings['host']+"/add-"+uri, data = newRoom)
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.post(self.__config_settings['host']+"/add-"+uri, data = newRoom)
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
            
            end = False
            while not end:
                # Insert Room Number
                roomID = int(input("Please insert the ID of room to search: "))
                isCommon_str = input("Is it common [Y/N]? ")

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
                    print("Room found!")
                    json.dumps(r.json(), indent=4)
                    
                # Otherwise, retry or cancel the command
                else:
                    if nattempts == 5 and str(r.status_code).startswith('5'):
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

            end = False
            while not end:
                # Insert Room Number
                roomID = int(input("Please insert the ID of the room to edit: "))
                isCommon_str = input("Is it common [Y/N]? ")

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
                    print("Room found!")
                    room = r.json()
                    json.dumps(room, indent=4)

                    # Ask for the new room number
                    newRoomID = int(input("Please insert the new ID of the room to edit: "))
                    
                    room['roomID_old'] = room['roomID']
                    room['roomID'] = newRoomID
                    
                    # Update the Room ID
                    nattempts = 1
                    r = requests.put(self.__config_settings['host']+"/update-"+uri, data=room)

                    while nattempts < 5 and str(r.status_code).startswith('5'):
                        nattempts += 1
                        r = requests.put(self.__config_settings['host']+"/update-"+uri, data=room)
                        
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
                    if nattempts == 5 and str(r.status_code).startswith('5'):
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
        r = requests.get(self.__config_settings['host']+"/room-list")
        nattempts = 1
        
        while nattempts < 5 and str(r.status_code).startswith('5'):
            r = requests.get(self.__config_settings['host']+"/room-list")
            nattempts += 1

        if r.status_code == requests.codes.ok:
            print("Registered Rooms and their content:")
            print(json.dumps(r.json(), indent=4))

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
            print(json.dumps(r.json(), indent=4))

        else:
            if nattempts == 5 and str(r.status_code).startswith('5'):
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
                    print("Room found!")
                    room = r.json()
                    json.dumps(room, indent=4)

                    # If so, and if there is no patient inside, ask for confirmation
                    if isCommon_str == 'Y' or isCommon_str == 'y' or len(room['patients']) == 0:
                        confirm_reply = input("Are you sure you want to delete this user [Y/N]? ")
                        
                        # Delete or not depending on confirmation reply
                        if confirm_reply == 'Y' or confirm_reply == 'y':

                            r = requests.delete(self.__config_settings['host']+"/delete-"+uri+"/"+str(roomID))
                            nattempts = 1

                            while nattempts < 5 and str(r.status_code).startswith('5'):
                                r = requests.delete(self.__config_settings['host']+"/delete-"+uri+"/"+str(roomID))                          
                                nattempts += 1

                            if r.status_code == requests.codes.ok:
                                print("User deleted!")
                                end = True
                            else:
                                if nattempts == 5:
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
                r = requests.post(self.__config_settings['host']+"/add-telegram-user/", data = json.dumps({
                    'user-id': userID,
                    'role' : role
                }))
                while nattempts < 5 and str(r.status_code).startswith('5'):
                    nattempts += 1
                    r = requests.post(self.__config_settings['host']+"/add-telegram-user/", data = json.dumps({
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
                
                # Look for the UserID in the Telegram ID List
                r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
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
                
                # Look for the UserID in the Telegram ID List
                r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                nattempts = 1

                while nattempts < 5 and str(r.status_code).startswith('5'):
                    r = requests.get(self.__config_settings['host'] + "/telegram-user/" + str(userID))
                    nattempts += 1

                # If present, ask for the new role
                if r.status_code == requests.codes.ok:

                    # Retrieve the new Role and check that it is meaningful
                    role = Role[input("Set the new role: ").upper()]

                    # Update the UserID in the Telegram ID List
                    nattempts = 1
                    r = requests.put(self.__config_settings['host']+"/update-telegram-user/", data = json.dumps({
                            'user-id': userID,
                            'role' : role
                        }))
                    while nattempts < 5 and str(r.status.code).startswith('5'):
                        nattempts += 1
                        r = requests.put(self.__config_settings['host']+"/update-telegram-user/", data = json.dumps({
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
                    print("User found!")
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
            print("Input not recognized! Retry.")

    def __updateService(self) :

        while self.__running :

            nwait = 0
            while nwait < 20 and self.__running:
                time.sleep(5)
                nwait += 1

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
        
        # Load settings
        config_file = open('./config.json')
        self.__config_settings = json.load(config_file)
        config_file.close()

        self.__running = True

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
        reply = input("Type anything to start: ")
    except TimeoutError:
        print('\r')
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



