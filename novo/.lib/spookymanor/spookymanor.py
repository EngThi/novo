from typing import Self
import sys
import time
import os

class _State:
    def __init__(self):
        self.current_room = None
        self.keys = []
        self.remaining_friends = []
        self.found_friends = []

    def set_current_room(self, room):
        self.current_room = room

state = _State()

def show_menu(options: list[str]) -> str:
    """
    Prints a list of options to the console and waits for the
    player to select one.

    Parameters:
        options (list[str]): A list of options to present to the player.

    Returns:
        str: The option selected by the player
    """

    while True:
        for i in range(0, len(options)):
            print(str(i + 1) + ") " + options[i])
        command = input().lower()
        try:
            num = int(command)
            if num > 0 and num <= len(options):
                print("")
                return options[num - 1]
            else:
                print("'" + str(num) + "' is not a valid choice.\n")
                continue
        except:
            pass

        try:
            index = [x.lower() for x in options].index(command)
            print("")
            return options[index]
        except:
            print("Try again. '" + command + "' is not a valid choice.\n")

def show_options(*options: list[str]) -> str:
    """
    Prints a list of options to the console and waits for the
    user to select one.

    Returns:
        str: The option selected by the player
    """
    return show_menu(options)

class Room:
    """
    A class representing a room that the player can be inside.

    Setting one of the direction properties (north, south, east, or west) will
    also update the room being set in the corresponding direction. For example,
    setting the north of a room will also set the south of the target room.

    Attributes:
        name (str): The name of the room
        description (str): A description of the room
        north (Room): The room to the North of this room or None if there is no room
        east (Room): The room to the East of this room or None if there is no room
        south (Room): The room to the South of this room or None if there is no room
        west (Room): The room to the West of this room or None if there is no room
        locked (bool): True if this room cannot be entered or False otherwise
        keys (list[Room]): A list of rooms that this room contains keys for
        friends (list[str]): A list of friends in this room
    """
    def __init__(self, name, description):
        self.name = name
        self.description = description
        self._north = None
        self._south = None
        self._east = None
        self._west = None
        self.locked = False
        self.keys = []
        self.friends = []

    def set_locked(self, locked: bool) -> None:
        """
        Sets whether this room is locked or not. If you wish to lock
        the room with a key, use add_key_for instead.

        Parameters:
            locked (bool): True to lock the room or False to unlock it
        """
        self.locked = locked
    
    def is_locked(self) -> bool:
        """
        Returns True if this room is locked and requires
        a key to enter.

        Returns:
            bool: True if the room is locked or False otherwise.
        """
        return self.locked == True
    
    def _get_north(self):
        return self._north
    def _set_north(self, room: Self):
        if self._north != None:
            self._north._south = None

        if room._south != None:
            room._south._north = None
        
        self._north = room
        room._south = self
    def _del_north(self):
        if self._north != None:
            self._north._south = None
        del self._north

    def _get_south(self):
        return self._south
    def _set_south(self, room: Self):
        if self._south != None:
            self._south._north = None

        if room._north != None:
            room._north._south = None
        
        self._south = room
        room._north = self
    def _del_south(self):
        if self._south != None:
            self._south._north = None
        del self._south

    def _get_east(self):
        return self._east
    def _set_east(self, room: Self):
        if self._east != None:
            self._east._west = None

        if room._west != None:
            room._west._east = None
        
        self._east = room
        room._west = self
    def _del_east(self):
        if self._east != None:
            self._east._west = None
        del self._east

    def _get_west(self):
        return self._west
    def _set_west(self, room: Self):
        if self._west != None:
            self._west._east = None

        if room._east != None:
            room._east._west = None
        
        self._west = room
        room._east = self
    def _del_west(self):
        if self._west != None:
            self._west._east = None
        del self._west

    north = property(_get_north, _set_north, _del_north)
    south = property(_get_south, _set_south, _del_south)
    east = property(_get_east, _set_east, _del_east)
    west = property(_get_west, _set_west, _del_west)
    
    def move(self, direction: str) -> None:
        """
        Moves the player character to the room in the given direction.
        Direction must be one of "North", "East", "South", or "West".
        If there is no room in the given direction or the room in that
        direction is locked, this will print a message and do nothing.

        Parameters:
            direction (str): One of either "North", "East", "South", or "West"
        """
        room = None
        match direction.lower():
            case "north":
                room = self._north
            case "east":
                room = self._east
            case "west":
                room = self._west
            case "south":
                room = self._south

        if room == None:
            print("You can't move there")
            return

        if room.is_locked():
            found_key = False
            for key in state.keys:
                if key == room:
                    print("\U0001F5DD " +  green_text(" You unlocked the door with the " + key.name + " key."))
                    found_key = True
                    break
            if not found_key:
                print("\U0001F512 You turn the handle, but the door is " + red_text("locked") + "! You need a key to enter this room.")
                return

        print("You walk into the " + room.name + ". " + red_text("The door slams shut behind you.") + "\n" + room.description)
        set_current_room(room)
        
    def show_move_options(self) -> None:
        """
        Prints a list of valid move directions to the console and
        waits for the player to make a choice. After choosing, the
        player will be moved to the room in the given direction.
        """
        options = []
        if self._north != None:
            options.append("North")
        if self._south != None:
            options.append("South")
        if self._east != None:
            options.append("East")
        if self._west != None:
            options.append("West")
        
        print(underline_text("Where will you move next?"))
        choice = show_menu(options)
        print("")
        self.move(choice)
        print("")
    
    def where_am_i(self) -> None:
        print(self.description)

    def look_around(self) -> None:
        """
        Prints out the description of the room as well as any connected
        rooms. If there is a key in this room, the player will also pick
        it up.
        """
        print(self.description)

        if self._north != None:
            print("The " + self._north.name + " is to the North.")
        if self._south != None:
            print("The " + self._south.name + " is to the South.")
        if self._east != None:
            print("The " + self._east.name + " is to the East.")
        if self._west != None:
            print("The " + self._west.name + " is to the West.")

        if len(self.keys) > 0:
            print("")
            for key in self.keys:
                print("\U0001F389 " + yellow_text("Congratulations! As you look around, you find the " + key.name + " key!"))
                state.keys.append(key)
            self.keys = []

        if len(self.friends) > 0:
            print("")
            for friend in self.friends:
                print("\U0001F388 " + yellow_text("You found your friend, " + friend + "!"))
                print(friend + " is now following you.")
                state.found_friends.append(friend)
                state.remaining_friends.remove(friend)
            self.friends = []
        
        print("")
    
    def add_key_for(self, room: Self) -> None:
        """
        Places a key for the given room in this room. That room will be locked
        to the player unless they first use the look_around function in this room
        to find the key.

        Parameters:
            room (Room): The room to lock and add a key for
        """
        self.keys.append(room)
        room.set_locked(True)
    
    def add_friend(self, name: str) -> None:
        """
        Places a friend in this room. The player will find the friend
        if they use the look_around function in this room.

        Parameters:
            name (str): The name of the friend
        """
        self.friends.append(name)
        state.remaining_friends.append(name)
    
def set_current_room(room: Self) -> None:
    """
    Sets the current room the player is in to the given room.

    Parameters:
        room (Room): The room to place the player in.
    """
    state.set_current_room(room)

def get_current_room() -> Room:
    """
    Gets the room the player is currently occupying.

    Returns:
        Room: The room the player is currently occupying.
    """
    return state.current_room

def remaining_friends() -> int:
    """
    Gets the number of friends that have not yet been found

    Returns:
        int: The number of friends reamining to find.
    """
    return len(state.remaining_friends)

def print_slow(str):
    """
    Slows down the return of text to appear like a typewriter.
    """
    for letter in str:
        sys.stdout.write(letter)
        sys.stdout.flush()
        time.sleep(0.005)

def enter_the_manor():
    # clear the screen
    print('\x1b[2J\x1b[3J\x1b[H')
    print_slow("While walking home from the movie theater with your three friends, you stop in front of an old house \nthat you don't remember seeing before. You and your friends decide to each explore the many rooms of \nthe house, but you soon realize that " + yellow_text("the house is not as normal as it seems") + ". \n\nYou need to explore the different rooms of the house, find your friends and hidden items, and avoid \nbeing caught by the mysterious owner of the house. Along the way, you will also find keys that will \nunlock some of the rooms. Be careful, though, as some rooms may contain " + green_text("surprises") + " or " + pink_text("challenges") + " \nthat could make the game more fun or more difficult.\n\n"+ bold_text("\U0001F47B " + red_text("Can you find all your friends and escape from the house before dawn?") + "\U0001F47B\n\n"))
    get_current_room().where_am_i()

def found_a_ghost():
    print_slow(r"""
                      .-.
         VS Code      /aa \_
                   __\-  / )                 .-.
         .-.      (__/    /    for EDU     _/oo \
       _/ ..\       /     \               ( \v  /__
      ( \  u/__    /       \__             \/   ___)
       \    \__)   \_.-._._   )  .-.       /     \
       /     \             `-`  / ee\_    /       \_
    __/       \               __\  o/ )   \_.-.__   )
   (   _._.-._/     Hour     (___   \/           '-'
    '-'                        /     \
                             _/       \    of Code
                            (   __.-._/
                              """)
    print("\n\n")

def red_text(str):
    return "\033[1;31m" + str + "\033[0;0m"

def green_text(str):
    return "\033[1;32m" + str + "\033[0;0m"

def yellow_text(str):
    return "\033[1;33m" + str + "\033[0;0m"

def blue_text(str):
    return "\033[1;34m" + str + "\033[0;0m"

def pink_text(str):
    return "\033[1;35m" + str + "\033[0;0m"

def underline_text(str):
    return "\033[4;37m" + str + "\033[0;0m"

def bold_text(str):
    return "\033[1;37m" + str + "\033[0;0m"