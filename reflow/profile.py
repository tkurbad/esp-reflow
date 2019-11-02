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

from reflow.menu import BaseMenu, MainMenu


class ReflowProfile():
    """ Class for Holding Data of a Single Reflow Profile. """
    def __init__(self, name = None, entries = []):
        self._name = name
        self._entries = entries
        self.line_num = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def entries(self):
        return self._entries

    def append_entry(self, line):
        # Empty line?
        if not line.strip():
            return
        linesplit = line.split(',')
        if len(linesplit) != 3:
            raise ValueError('Profile syntax error in line {0:d}'.format(self.line_num))

        try:
            intline = [int(i.strip()) for i in linesplit]
        except ValueError:
            raise ValueError('Non numeric value in profile line {0:d}'.format(self.line_num))

        self.line_num += 1
        self.entries.append(intline)

    def __len__(self):
        return len(self.entries)


class ProfileControl:
    """ Class for Handling Reflow Profiles for Different Solder Alloys.
    """

    def __init__(self, sdcard, current_profile = None, extension = None):
        """ Initialize Reflow Profile Class. """
        self.sdcard             = sdcard
        self.extension          = extension
        if extension is None:
            self.extension      = DEFAULT_PROFILE_EXT
        self.profiles           = []
        self.current_profile    = current_profile
        self.buf                = bytearray(250)
        self._err                = None

    def listProfiles(self, extension = None):
        if extension is None:
            extension = self.extension

        try:
            self.profiles = self.sdcard.listFiles(extension = extension)
            return len(self.profiles)
        except OSError as e:
            if 'sd card not mounted' in '{}'.format(e.args[0].lower()):
                self._err = e.args[0]
                self.profiles = []
            else:
                raise (e)

        self.profiles = sorted(self.profiles)
        return len(self.profiles)

    def readProfile(self, profile_path, save = True):
        profile_len = 0
        with open(profile_path) as profile:
            profile_len = profile.readinto(self.buf)
            profile_lines = self.buf[:profile_len].decode().splitlines()

        temp_profile = ReflowProfile()
        # Profile Name
        temp_profile.name = profile_lines[0]

        # Profile Entries (Setpoint, Soaktime, Overshoot_Prevention_Strength)
        for profile_line in profile_lines[1:]:
            try:
                temp_profile.append_entry(profile_line)
            except ValueError as e:
                self._err = e.args[0]
                self.current_profile = None
                return

        # Success!
        self.current_profile = temp_profile
        if save:
            self.setCurrentProfileAsDefault()

    def getDefaultProfile(self, default_filename = None):
        if default_filename is None:
            default_filename = DEFAULT_PROFILE_FILE
        try:
            stat(default_filename)
        except OSError as e:
            if e.args[0] == 2:
                self._err = 'Default profile not found'
                return None
            else:
                raise(e)

        self.readProfile(default_filename, save = False)

    def setCurrentProfileAsDefault(self, default_filename = None):
        if self.current_profile is None or len(self.current_profile) == 0:
            return

        if default_filename is None:
            default_filename = DEFAULT_PROFILE_FILE
        with open(default_filename, 'w') as def_profile:
            def_profile.write('{}\n'.format(self.current_profile.name))
            for (sp, st, op) in self.current_profile.entries:
                def_profile.write('{},{},{}\n'.format(sp, st, op))

    @property
    def err(self):
        err = self._err
        self._err = None
        return err


class ProfileLoaderMenu(BaseMenu):
    """ File List Display for Loading a Profile from SD Card. """
    paused = False      # Pause Menu Display
    was_paused = False  # Was the Menu Display Paused During the Last Cycle

    def __init__(self, profile_control, display, rotary,
                 button_up = None, button_down = None,
                 button_left = None, button_right = None, lock = None):
        ProfileLoaderMenu.paused = True
        self.profile_control = profile_control
        entries = []
        self.mountpoint = self.profile_control.sdcard.mountpoint

        super(ProfileLoaderMenu, self).__init__(
            entries, display, rotary, button_up, button_down,
            button_left, button_right, lock)

    def draw_items(self):
        """ (Re-)Draw All Profiles Currently on SD Card, Highlighting
            the Currently Active One.
        """
        if ProfileLoaderMenu.paused:
            return

        entries = [['< Back to Main Menu', self.cb_go_back, None]]
        mountpoint = self.mountpoint

        profile_count = self.profile_control.listProfiles()
        for profile in self.profile_control.profiles:
            entries.append([profile,
                            self.cb_read_profile,
                            '{}/{}'.format(mountpoint, profile)
                            ])

        super(ProfileLoaderMenu, self).__init__(
            entries, self.display, self.rotary, self.button_up,
            self.button_down, self.button_left, self.button_right,
            self.lock)

        self.clear()
        for index in range(0, self.num_items):
            self.draw_item(index)
        collect()

    def _draw_item(self, index):
        """ Draw a Single Menu Item with Number 'index'. """
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
        # Extract the Values from the item at 'index'
        (title, callback, params) = self.items[index]
        self.display.set_font(MENU_FONT)
        self.display.chars(title,
                           MENU_START_X + MENU_ITEM_OFFSET,
                           MENU_START_Y + MENU_ITEM_OFFSET + (index * MENU_ITEM_SPACING_Y))

    def callback_item(self, index):
        """ Run the Callback Function of Menu Item at 'index'. """
        (title, callback, params) = self.items[index]
        if callback is None:
            return
        if params is None:
            callback()
        else:
            callback(params)
        sleep_ms(50)
        self.draw_item(index)

    def cb_go_back(self):
        ProfileLoaderMenu.paused = True
        MainMenu.was_paused = True
        MainMenu.paused = False

    def cb_read_profile(self, profile_path):
        self.profile_control.readProfile(profile_path)
        self.cb_go_back()
