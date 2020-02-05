# Main Execution File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect, mem_alloc, mem_free, threshold
from _thread import allocate_lock, start_new_thread

from machine import reset
from micropython import alloc_emergency_exception_buf, mem_info
from utime import sleep_ms

from config import THERMOCOUPLE_BUSID, THERMOCOUPLE_BAUDRATE
from config import THERMOCOUPLE_NAME1, THERMOCOUPLE_NAME2, THERMOCOUPLE_NAME3
from config import THERMOCOUPLE_CS1, THERMOCOUPLE_CS2, THERMOCOUPLE_CS3

from display.basic import Display
from thermocouple.thermocouple import Thermocouple
from reflow.device import ButtonDown, ButtonLeft, ButtonRight, ButtonUp
from reflow.device import Buzzer, Fan, HeaterBottom, HeaterTop, Light
from reflow.device import RotaryEncoder, SDCardHandler
from reflow.error import ReflowError
from reflow.menu import MainMenu
from reflow.profile import ProfileControl, ProfileLoaderMenu
from reflow.reflow import HeatControl
from wlan_sta import STA

##
## Setup
##
# Buffer Exceptions
alloc_emergency_exception_buf(100)

# Initialize Display
tft = Display()
tft.prepare()

# Set Up Light Switch
light = Light()

# Initialize SPI bus for thermocouples
thermocouples = Thermocouple(busid = THERMOCOUPLE_BUSID,
                             baudrate = THERMOCOUPLE_BAUDRATE)

# Set up thermocouples
thermocouples.add_tc(name = THERMOCOUPLE_NAME1,
                     cs = THERMOCOUPLE_CS1)
thermocouples.add_tc(name = THERMOCOUPLE_NAME2,
                     cs = THERMOCOUPLE_CS2)
thermocouples.add_tc(name = THERMOCOUPLE_NAME3,
                     cs = THERMOCOUPLE_CS3)

# Get and Display IP Address
ipaddress = STA().ipaddress
tft.show_ipaddress(ipaddress)

# Set Up Buzzer
buzzer = Buzzer()

# Set Up Top Heater
heater_top = HeaterTop()

# Set Up Bottom Heater
heater_bottom = HeaterBottom()

# Set Up Fan
fan = Fan()

# Set Up Rotary Encoder
rotary = RotaryEncoder()

# Set Up the Push Buttons
button_up = ButtonUp()
button_left = ButtonLeft()
button_right = ButtonRight()
button_down = ButtonDown()

sleep_ms(500)

# Allocate a lock
reflowLock = allocate_lock()

# Initialize and Try to Mount SD Card
sdcard = SDCardHandler(lock = reflowLock)

threshold(mem_free() // 4 + mem_alloc())
collect()

sdcard.mount()

# Profile Control Object
profile_control = ProfileControl(sdcard)

# Try to Get Current Profile
profile_control.getDefaultProfile()
current_profile = profile_control.current_profile

# Heat Control Object
heat_control = HeatControl(lock = reflowLock,
                           thermocouples = thermocouples,
                           heater_top = heater_top,
                           heater_bottom = heater_bottom,
                           fan = fan,
                           reflow_profile = current_profile,
                           buzzer = buzzer,
                           light = light)

collect()


##
## Basic Threads
##
def statusDisplayThread(lock):
    """ Display Status, i.e. IP-Address and Temperatures on TFT. """
    global ipaddress, sdcard
    with lock as l:
        tft.show_ipaddress(ipaddress)

    while True:
        with lock as l:
            tft.show_temperatures(thermocouples.temp)
            tft.show_heaters(heat_control.heater_duty)
            tft.show_profile(heat_control.reflow_profile)
            error_message = ReflowError.getError()[0]
            if error_message is not None:
                tft.show_error(error_message)
            if ipaddress != STA().ipaddress:
                ipaddress = STA().ipaddress
                tft.show_ipaddress(ipaddress)
            tft.show_fan(fan.duty())
            tft.show_light(light.pin.value())
            tft.show_sdcard(sdcard.is_mounted())
        sleep_ms(100)


def buttonThread():
    # For now, just duplicate/emulate the rotary encoder
    while True:
        sleep_ms(50)
        if button_up.value():
            if rotary._value > rotary._min_val:
                rotary._value -= 1
            continue
        if button_down.value():
            if rotary._value < rotary._max_val:
                rotary._value += 1
            continue
        if button_left.value():
            print('Left')
            continue
        if button_right.value():
            rotary._button_pressed = True

    

# Start Reading Heat Values (with Locking - Lock Variable Given During Init)
start_new_thread(heat_control.heatReadResponse, ())

# Start Displaying Status (with Locking)
start_new_thread(statusDisplayThread, (reflowLock, ))

# Start Reading Button Presses (without Locking)
#start_new_thread(buttonThread, ())

##
## Main Menu
##

## Callback Functions
# Profile Loader Menu Display
def profiles():
    MainMenu.paused = True
    ProfileLoaderMenu.was_paused = True
    ProfileLoaderMenu.paused = False
    profile_loader_menu.loop(exit_on_pause = True)
    error_message = ReflowError.getError()[0]
    if error_message is not None:
        tft.show_error(error_message)
    if profile_control.current_profile != current_profile:
        heat_control.reflow_profile = profile_control.current_profile


# Define Main Menu Items
#  Format:
#   [show_title2, title1, callback1, arguments1, title2, callback2, arguments2]
#
#   Explanation of the Fields:
#
#   - show_title2: Boolean or Callable that Denotes whether to Show title1 or title2
#                  and whether to Activate callback1(arguments1) or callback2(arguments2)
#                  Respectively.
#                  For Static Entries, Use Booleans. For Dynamic Menu Entry
#                  Toggling, a Callable Should be Used.
#
#   - title1     : Menu Item Title that is Displayed if show_title2 is False.
#
#   - callback1  : Callback Function that is Activated by Choosing the Menu
#                  Item while title1 is Active.
#
#   - arguments1 : Tuple with Arguments to callback1 (or None for no Arguments).
#
#   - title2     : Menu Item Title that is Displayed if show_title2 is True.
#
#   - callback2  : Callback Function that is Activated by Choosing the Menu
#                  Item while title2 is Active.
#
#   - arguments2 : Tuple with Arguments to callback2 (or None for no Arguments).
#
#
# Example Static Main Menu Item
#  calibrate = [False, 'Calibrate', calibrate, ('x', 1), None, None, None]
#
# Example Dynamic Main Menu Item
#  sdcard = [sd_card_mounted, 'Mount SD Card', mount_sd, None, 'Unmount SD Card', umount_sd, None]

main_menuitems = [
    [False, 'Load Profile from SD', profiles, None, None, None, None],
    [HeatControl.isReflowing, 'Start Reflow Process', heat_control.startReflow, None, 'Stop Reflow Process', heat_control.cancelReflow, None],
    [light.pin.value, 'Turn on Light', light.pin.on, None, 'Turn off Light', light.pin.off, None],
    [sdcard.is_mounted, 'Mount SD Card', sdcard.mount, None, 'Unmount SD Card', sdcard.umount, None],
    [False, 'Restart', reset, None, None, None, None],
]

# Set Up Main Menu
main_menu = MainMenu(main_menuitems, tft, rotary, lock = reflowLock)
# Trigger Initial Display of Menu Items
MainMenu.was_paused = True

# Set Up Profile Loader Menu
profile_loader_menu = ProfileLoaderMenu(profile_control,
                                        tft,
                                        rotary,
                                        lock = reflowLock
                                        )


# Print Memory Info
mem_info()

##
## Main Code
##
try:
    """ Handle Menu Input. """
    main_menu.loop()
except:
    raise
finally:
    """ Deinitialize all PWM and SPI Devices.
        !!! Disable Heaters First to Prevent Fires !!!
    """
    heater_bottom.deinit()
    heater_top.deinit()
    fan.deinit()
    buzzer.deinit()
    sdcard.deinit()
