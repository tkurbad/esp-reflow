# Profile Read/Processing Classes for ESP32 Micropython Driven SMD
#  Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect

from uos import ilistdir, stat
from utime import sleep_ms

from config import DEFAULT_PROFILE_FILE, DEFAULT_PROFILE_EXT, DEFAULT_SD_MOUNTPATH
from config import MENU_WIDTH, MENU_START_X, MENU_START_Y
from config import MENU_FONT, MENU_ITEM_OFFSET, MENU_ITEM_SPACING_Y
from config import MENU_ACTIVE_ITEM_COLOR, MENU_ACTIVE_BG_COLOR
from config import MENU_INACTIVE_ITEM_COLOR, MENU_INACTIVE_BG_COLOR

from reflow.error import ReflowError
from reflow.menu import BaseMenu, MainMenu


class ReflowProfile():
    """ Class for Holding Data of a Single Reflow Profile. """
    def __init__(self, name = None, entries = []):
        self._name      = name
        self._entries   = entries
        self.line_num   = 0

    @property
    def name(self):
        """ Get the Name of the Profile. """
        return self._name

    @name.setter
    def name(self, name):
        """ Set the Name of the Profile. """
        self._name = name

    @property
    def entries(self):
        """ Get the Profile's Entries.

            Returns a List of Lists of the Form
            [temperature_setpoint, soaktime, overshoot_prevention_steps]
        """
        return self._entries

    def append_entry(self, line):
        """ Append an Entry to the List of the Profile's Entries.

            'line' is a String of the Form
            "temperature_setpoint, soaktime, overshoot_prevention_steps"

            Whitespaces are Allowed. All Values Have to Evaluate as
            Integers.
        """
        # Empty Line?
        if not line.strip():
            return

        linesplit = line.split(',')
        if len(linesplit) != 3:
            # Line Does not Have 3 Comma-Separated Elements.
            raise ValueError('Profile syntax error in line {0:d}'.format(self.line_num))

        try:
            # Parse Split Line into List of 3 Integers.
            intline = [int(i.strip()) for i in linesplit]
        except ValueError:
            raise ValueError('Non numeric value in profile line {0:d}'.format(self.line_num))

        self.line_num += 1      # For Possible Error Messages Upon Next Append
        self.entries.append(intline)

    def __len__(self):
        """ Return Length of Profile, i.e. Number of Entries. """
        return len(self.entries)


class ProfileControl:
    """ Class for Handling Reflow Profiles for Different Solder Alloys.
    """

    def __init__(self, sdcard, current_profile = None, extension = None):
        """ Initialize Reflow Profile Class. """
        self.sdcard             = sdcard
        self.extension          = extension
        if extension is None:
            self.extension      = DEFAULT_PROFILE_EXT   # Default File Extension
        self.profiles           = []                # Buffer for Profiles on SD
        self.current_profile    = current_profile
        self.buf                = bytearray(250)    # Buffer for Profile Content

    def listProfiles(self, extension = None):
        """ Store a List of All Profiles that Are on the SD Card in
            self.profiles. Return the Number of Profiles Found.
        """
        # Filename Extension
        if extension is None:
            extension = self.extension

        try:
            # Use the listFiles Method from the SDCard Class.
            self.profiles = self.sdcard.listFiles(extension = extension)
            return len(self.profiles)
        except OSError as e:
            # Something Went Wrong.
            if 'sd card not mounted' in '{}'.format(e.args[0].lower()):
                # No SD Card Has Been Mounted. Display Error and Continue.
                ReflowError.setError('No SD Card', e)
                print(e)
                self.profiles = []
            else:
                # Something Unexpected Happened. Raise Exception
                raise (e)

        # Sort Profiles Alphabetically.
        self.profiles = sorted(self.profiles)
        # Return the Number of Available Profiles.
        return len(self.profiles)

    def readProfile(self, profile_path, save = True):
        """ Read the Given Profile from SD Card and Set It as Current
            Profile.

            If 'save == True' also Store the Profile as Default to the
            Internal Flash Memory of the Device. This Profile Will
            Henceforth be Available Immediately after Poweron.
        """
        profile_len = 0
        with open(profile_path) as profile:
            # Read the Profile File Contents into 'self.buf'.
            profile_len = profile.readinto(self.buf)
            # Split the Relevant Portion of the Buffer into Separate Lines.
            profile_lines = self.buf[:profile_len].decode().splitlines()

        # Create a New Profile Object.
        temp_profile = ReflowProfile()
        # Set Profile Name.
        temp_profile.name = profile_lines[0]

        # Set. Profile Entries (Setpoint, Soaktime, Overshoot_Prevention_Strength)
        for profile_line in profile_lines[1:]:
            try:
                temp_profile.append_entry(profile_line)
            except ValueError as e:
                ReflowError.setError('Wrong Profile Format', e)
                print(e)
                self.current_profile = None
                return

        # Success! Activate the Profile...
        self.current_profile = temp_profile
        if save:
            # ... and Save it as On-Device Default.
            self.setCurrentProfileAsDefault()

    def getDefaultProfile(self, default_filename = None):
        """ Read the Currently Set Default Profile from the Device's
            Flash Memory.
        """
        if default_filename is None:
            default_filename = DEFAULT_PROFILE_FILE
        try:
            # Is a Profile Saved, i.e. Does the Default File Exist?
            stat(default_filename)
        except OSError as e:
            if e.args[0] == 2:
                # No Saved Profile Has Been Found.
                ReflowError.setError('No Default Profile', e)
                return None
            else:
                # Something Else Went Wrong.
                raise(e)

        # Read the Default Profile.
        self.readProfile(default_filename, save = False)

    def setCurrentProfileAsDefault(self, default_filename = None):
        """ Save the Current Profile as Default to the Device's Flash
            Memory.
        """
        if self.current_profile is None or len(self.current_profile) == 0:
            # There Is No Current Profile.
            return

        if default_filename is None:
            default_filename = DEFAULT_PROFILE_FILE
        with open(default_filename, 'w') as def_profile:
            # Recreate the File Contents from the Current ReflowProfile
            #   Object.
            def_profile.write('{}\n'.format(self.current_profile.name))
            for (sp, st, op) in self.current_profile.entries:
                def_profile.write('{},{},{}\n'.format(sp, st, op))


class ProfileLoaderMenu(BaseMenu):
    """ File List Display for Loading a Profile from SD Card. """
    paused = False      # Pause Menu Display
    was_paused = False  # Was the Menu Display Paused During the Last Cycle

    def __init__(self, profile_control, display, rotary,
                 button_up = None, button_down = None,
                 button_left = None, button_right = None, lock = None):
        ProfileLoaderMenu.paused = True # Should Be Paused by Default.
        self.profile_control = profile_control
        entries = []
        self.mountpoint = self.profile_control.sdcard.mountpoint

        # Initialize the Base Class.
        super(ProfileLoaderMenu, self).__init__(
            entries, display, rotary, button_up, button_down,
            button_left, button_right, lock)

    def draw_items(self):
        """ (Re-)Draw All Profiles Currently on SD Card, Highlighting
            the Currently Active One.
        """
        if ProfileLoaderMenu.paused:
            return

        # First Entry is Always a Callback to Go Back to the Main Menu
        entries = [['< Back to Main Menu', self.cb_go_back, None]]
        mountpoint = self.mountpoint

        # How Many Profiles Have to Be Displayed?
        profile_count = self.profile_control.listProfiles()
        for profile in self.profile_control.profiles:
            # Create Menu Entries with
            #   [name, callback_function, callback_arguments]
            entries.append([profile,
                            self.cb_read_profile,
                            '{}/{}'.format(mountpoint, profile)
                            ])

        # Initialize the Base Class (Again) With the Given Entries.
        super(ProfileLoaderMenu, self).__init__(
            entries, self.display, self.rotary, self.button_up,
            self.button_down, self.button_left, self.button_right,
            self.lock)

        # Clear the Display Portion Reserved for the Menu.
        self.clear()
        # Draw All Entries to the Display.
        for index in range(0, self.num_items):
            self.draw_item(index)

        # Do a Garbage Collection
        collect()

    def _draw_item(self, index):
        """ Draw a Single Profile Entry with Number 'index'. """
        if index == self.active:
            # Item Is Currently Active - Set Colors Accordingly and
            # Draw Active Item Background
            self.display.set_color(MENU_ACTIVE_ITEM_COLOR,
                                   MENU_ACTIVE_BG_COLOR)
            self.display.fill_rectangle(MENU_START_X,
                                        MENU_START_Y + MENU_ITEM_OFFSET + (index * MENU_ITEM_SPACING_Y),
                                        MENU_WIDTH,
                                        MENU_FONT.height(),
                                        color = MENU_ACTIVE_BG_COLOR)
        else:
            # Menu Item is Inactive - Set Colors Accordingly and Clear
            # Item Background
            self.display.set_color(MENU_INACTIVE_ITEM_COLOR,
                                   MENU_INACTIVE_BG_COLOR)
            self.display.fill_rectangle(MENU_START_X,
                                        MENU_START_Y + MENU_ITEM_OFFSET + (index * MENU_ITEM_SPACING_Y),
                                        MENU_WIDTH,
                                        MENU_FONT.height(),
                                        color = MENU_INACTIVE_BG_COLOR)
        # Extract the Values from the Item at 'index'
        (title, callback, params) = self.items[index]
        self.display.set_font(MENU_FONT)
        self.display.chars(title,
                           MENU_START_X + MENU_ITEM_OFFSET,
                           MENU_START_Y + MENU_ITEM_OFFSET + (index * MENU_ITEM_SPACING_Y))

    def callback_item(self, index):
        """ Run the Callback Function of Profile Entry at 'index'. """
        # Extract the Components of the Entry.
        (title, callback, params) = self.items[index]
        if callback is None:
            return
        if params is None:
            # Callback without Arguments.
            callback()
        else:
            # Callback with Arguments.
            callback(params)

        # This Will Only be Called if Something Went Wrong.
        sleep_ms(50)
        # Redraw Item.
        self.draw_item(index)

    def cb_go_back(self):
        """ Callback Method that Points Back to the Main Menu. """
        # Pause this 'Menu'.
        ProfileLoaderMenu.paused = True
        # Unpause the Main Menu.
        MainMenu.was_paused = True
        MainMenu.paused = False

    def cb_read_profile(self, profile_path):
        """ Read a Profile from SD Card and Go Back to the Main Menu.
        """
        self.profile_control.readProfile(profile_path)
        self.cb_go_back()
