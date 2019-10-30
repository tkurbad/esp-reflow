# Profile Read/Processing Classes for ESP32 Micropython Driven SMD
#  Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect

from ujson import dump, load
from uos import ilistdir, stat

from config import DEFAULT_PROFILE_FILE, DEFAULT_PROFILE_EXT, DEFAULT_SD_MOUNTPATH

class ReflowProfile:
    """ Class for Holding Data of a Single Reflow Profile. """
    def __init__(self, name = None, entries = []):
        self._name = name
        self._entries = entries
        self.entry_index = 0

    def reset(self):
        self.entry_index = 0

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        self._name = name

    @property
    def next_entry(self):
        try:
            self.entry_index += 1
            return self._entries[self.entry_index]
        except IndexError:
            return None

    def append_entry(self, line):
        linesplit = line.split(',')
        if len(linesplit) != 3:
            raise ValueError('Profile syntax error in line {0:d}'.format(index))

        try:
            intline = [int(i.strip()) for i in line]
        except ValueError:
            raise ValueError('Non numeric value in profile line {0:d}'.format(index))

        self.entries.append(intline)


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
        self.err                = None

    def listProfiles(self, extension = None):
        if extension is None:
            extension = self.extension

        try:
            self.profiles = self.sdcard.listFiles(extension = extension)
            return len(self.profiles)
        except OSError as e:
            if 'sd card not mounted' in '{}'.format(e.args[0].lower()):
                self.err = e.args[0]
                self.profiles = []
            else:
                raise (e)

        return len(self.profiles)

    def readProfile(self, profile_path):
        profile_len = 0
        with open(profile_path) as profile:
            profile_len = profile.readinto(self.buf)
            profile_lines = self.buf[:profile_len].decode.splitlines()

        temp_profile = ReflowProfile()
        # Profile Name
        temp_profile.name = profile_lines[0]

        # Profile Entries (Setpoint, Soaktime, Overshoot_Prevention_Strength)
        index = 0
        profile_lines_num = len(profile_lines)
        while index < profile_lines_num:
            index += 1
            try:
                temp_profile.append_entry(profile_lines[index])
            except ValueError as e:
                self.err = e.args[0]
                self.current_profile = None
                return

        # Success!
        self.current_profile = temp_profile

    def getDefaultProfile(self, default_filename = None):
        if default_filename is None:
            default_filename = DEFAULT_PROFILE_FILE
        try:
            stat(default_filename)
        except OSError as e:
            if e.args[0] == 2:
                self.err = 'Default profile not found'
                return None
            else:
                raise(e)

        with open(default_filename) as def_profile:
            self.current_profile = load(def_profile)

    def setCurrentProfileAsDefault(self, default_filename = None):
        if default_filename is None:
            default_filename = DEFAULT_PROFILE_FILE
        with open(default_filename, 'w') as def_profile:
            dump(self.current_profile, def_profile)
