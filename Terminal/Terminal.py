import requests
import json
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

    def __init__(self):
        config_file = open('config.json')
        self.__config_settings = json.load(config_file)
        config_file.close()

    def __handle_command(self, command: Command, command_type: CommandType):
        
        if command_type == CommandType.ROOM:

            # Add Room
            if command == Command.ADD:
                # Insert Room Number
                # Check if it is already taken
                # If not, add the room
                # Otherwise, cancel the command
                pass

            # Search Room
            elif command == Command.SEARCH:
                # Insert Room Number
                # Check if it exists
                # If so, show it, the patients inside and the sensors
                # Otherwise, cancel the command
                pass

            # Edit Room
            elif command == Command.EDIT:
                # Insert Room Number
                # Check if it exists
                # If so, show it, the patients inside and the sensors
                #     and ask for the new room number
                # Otherwise, cancel the command
                pass

            # Show Room
            elif command == Command.SHOW:
                # Show all rooms, the patients inside and the sensors
                pass

            # Delete Room
            elif command == Command.DELETE:
                # Insert Room Number
                # Check if it exists
                # If so, and if there is no patient inside, ask for confirmation
                # Otherwise, if the room has patients inside, cancel the command
                # If the room does not exist, cancel the command
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
                self.__user_telegram.show()

            # Delete User
            elif command == Command.DELETE:
                self.__user_telegram.delete()

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

    def __room_add(self):
        pass

    def __room_search(self):
        pass      

    def __room_edit(self):
        pass       

    def __room_show(self):
        pass

    def __room_delete(self):
        pass

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
                r = requests.post(self.__config_settings['host']+"/add-telegram-user-id/", data = json.dumps({
                    'user-id': userID,
                    'role' : role
                }))
                if r.status_code == requests.codes.ok:
                    print("User added successfully!")
                    end = True
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

                # If present, show it
                if r.status_code == requests.codes.ok:
                    user = r.json()
                    print("User found!")
                    print("UserID: {userID}\n Role: {role}".format(userID=user['user-id'], role=user['role']))
                    end = True

                # Otherwise, notify that it does not exist
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
                r = requests.get(self.__config_settings['host'] + "/get-telegram-user-id/" + str(userID))

                # If present, ask for the new role
                if r.status_code == requests.codes.ok:

                    # Retrieve the new Role and check that it is meaningful
                    role = Role[input("Set the new role: ").upper()]

                    # Update the UserID in the Telegram ID List
                    nattempts = 0
                    while nattempts < 5 and r.status.code != requests.codes.ok:
                        nattempts += 1
                        r = requests.put(self.__config_settings['host']+"/update-telegram-user-id/", data = json.dumps({
                            'user-id': userID,
                            'role' : role
                        }))

                    if nattempts == 5 and r.status.code != requests.codes.ok:
                        print("Operation failed: Reached the max. number of attempts!")
                    else:
                        print("User updated successfully!")

                    end = True

                # Otherwise, notify that it does not exist
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
        nattempts = 0
        request = requests.get(self.__config_settings['host']+ "/telegram-user-id-list")
        while nattempts < 5 and request.status_code != requests.codes.ok:
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
                r = requests.get(self.__config_settings['host'] + "/get-telegram-user-id/" + str(userID))

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

                        if r.status_code == requests.codes.ok:
                            print("User deleted!")
                        else:
                            command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                            if command != 'q':
                                end = False

                    else:
                        print("Operation aborted.")

                # Otherwise, notify that it does not exist
                else:
                    command = input("Operation failed: User not found! Retry [r] or quit [q]: ")
                    if command == 'q':
                        end = True

        except (ValueError, KeyError):
            print("Input not recognized! Retry.")


if __name__ == '__main__':

    terminal = Terminal()
    
    # Register/Update Service
    pass

    # Launch Service
    terminal.launch()
    

