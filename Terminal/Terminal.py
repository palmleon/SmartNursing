from enum import Enum

class CommandType(Enum):
    ROOM = 0
    USER = 1 

class Command(Enum):
    ADD = 0
    SEARCH = 1
    EDIT = 2
    SHOW = 3
    DELETE = 4


class Terminal(object):

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

        elif command_type == CommandType.USER:
            # Add User
            if command == Command.ADD:
                # Insert User ID
                # Check if it is already taken
                # If not, add the user and their role
                # Otherwise, cancel the command
                pass
            # Search User
            elif command == Command.SEARCH:
                # Insert User Number
                # Check if it exists
                # If so, show them and their role
                # Otherwise, cancel the command
                pass

            # Edit User
            elif command == Command.EDIT:
                # Insert Room Number
                # Check if it exists
                # If so, show them and their role
                #     and ask for the new ID and role
                # Otherwise, cancel the command
                pass

            # Show User
            elif command == Command.SHOW:
                # Show all users and their IDs
                pass

            # Delete User
            elif command == Command.DELETE:
                # Insert User ID
                # Check if it exists
                # If so, ask for confirmation
                # Otherwise, if the user does not exist, cancel the command
                pass

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

                # Repeat

            except KeyError:
                print("-"*40)
                print("Command not recognized! Retry.")
                print("-"*40)

if __name__ == '__main__':
    terminal = Terminal()
    terminal.launch()
    

