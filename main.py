# Main Execution File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

import gc
import _thread

from machine import Pin, PWM, reset
from ucollections import deque
from uos import mount, umount
from utime import sleep, sleep_ms, ticks_diff, ticks_ms

import config

from display.basic import Display
from thermocouple.thermocouple import Thermocouple
from reflow.device import ButtonDown, ButtonLeft, ButtonRight, ButtonUp
from reflow.device import Buzzer, Fan, HeaterBottom, HeaterTop, Light
from reflow.device import RotaryEncoder, SDCardHandler
from reflow.menu import Menu
from reflow.reflow import HeatControl
from wlan_sta import STA

##
## Cache Some Configuration Variables
##
#FAN_LOW_DUTY            = config.FAN_LOW_DUTY
#FAN_HIGH_DUTY           = config.FAN_HIGH_DUTY
#FAN_LOW_DUTY_TEMP       = config.FAN_LOW_DUTY_TEMP
#FAN_HIGH_DUTY_TEMP      = config.FAN_HIGH_DUTY_TEMP
#HEATER_BOTTOM_MAX_DUTY  = config.HEATER_BOTTOM_MAX_DUTY
#HEATER_TOP_MAX_DUTY     = config.HEATER_TOP_MAX_DUTY
#HEATER_NAME_BOTTOM      = config.HEATER_NAME_BOTTOM
#HEATER_NAME_TOP         = config.HEATER_NAME_TOP

##
## Setup
##

# Initialize Display
tft = Display()
tft.prepare()

# Set Up Light Switch
light = Light()

# Initialize SPI bus for thermocouples
thermocouples = Thermocouple(busid = config.THERMOCOUPLE_BUSID,
                             baudrate = config.THERMOCOUPLE_BAUDRATE)

# Set up thermocouples
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME1,
                     cs = config.THERMOCOUPLE_CS1)
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME2,
                     cs = config.THERMOCOUPLE_CS2)
thermocouples.add_tc(name = config.THERMOCOUPLE_NAME3,
                     cs = config.THERMOCOUPLE_CS3)

pcb_thermocouple = config.THERMOCOUPLE_NAME3

# Set Up Variable to Display Duty Cycles
#heater_duty = {
#    config.HEATER_NAME_TOP: 0.0,
#    config.HEATER_NAME_BOTTOM: 0.0
#}

# Allocate a lock
reflowLock = _thread.allocate_lock()

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

# Heat Control Object
heat_control = HeatControl(reflowLock,
                           thermocouples,
                           heater_top,
                           heater_bottom,
                           fan,
                           None,
                           buzzer = buzzer,
                           light = light)
gc.collect()

# Let Device Settle
sleep(0.5)

# Initialize and Try to Mount SD Card
sdcard = SDCardHandler()
try:
    sdcard.mount()
except MemoryError:
    gc.collect()

# Variables Controlling the Actual Reflow Process
##do_reflow = False
##reflow_profile_table = deque((), 5, 1)
##soaking_started = 0.0


##
## Basic Threads
##

# # # This is the Central Thread that Does All the Thermocouple Readings and
# # # Heater Control
# # def heatReadResponseThread(lock):
    # # """ Read Heater PWM Duty Settings and Thermocouple Values Every
        # # 500 ms.
        # # If Heating is Requested by the global 'do_reflow', Do a
        # # "Bang Bang" Control of the Upper and Lower Heaters to Follow
        # # the Currently Loaded Reflow Profile.

        # # The Following Rule Applies for Each Temperature Setpoint in the
        # # Profile:

        # # 1) If New Setpoint > Current Setpoint: Heat Up as Fast as
                                               # # Possible
        # # 2) If Setpoint is Reached and Soak
                             # # Time is not Over: Keep Temperature by
                                               # # "Banging" the Heaters Off
                                               # # and On again with Reduced
                                               # # Power
        # # 3) If New Setpoint == 0 or No New SP:  Turn Heaters Off, Reset
                                               # # do_reflow = False, and
                                               # # set 'open_door' Alarm
                                               # # Flag to True
        # # 4) If New Setpoint > 0, but < Current
                                     # # Setpoint: Turn Off Heaters, Wait
                                               # # for Temperature to Reach
                                               # # New Setpoint, Start
                                               # # Soaking as in 2)
    # # """

    # # global heater_duty          # Heater duty values as read by the
                                # # # respective thread
    # # global do_reflow            # Do the actual reflow
    # # global reflow_profile_table # Simplified reflow profile as deque of
                                # # #  Tuples (temp_setpoint, temp_soaktime)
    # # global soaking_started

    # # last_setpoint = 0.0
    # # temp_setpoint = 0.0
    # # temp_soaktime = 0.0
    # # overshoot_prevention = 0
    # # current_overshoot_step = None
    # # heating_top = False
    # # heating_bottom = False

    # # def _shutoff(soft = False):
        # # global do_reflow
        # # global soaking_started
        # # nonlocal last_setpoint
        # # nonlocal temp_setpoint
        # # nonlocal temp_soaktime
        # # nonlocal overshoot_prevention
        # # nonlocal current_overshoot_step
        # # nonlocal heating_top
        # # nonlocal heating_bottom

        # # heater_top.duty(0)
        # # heater_bottom.duty(0)
        # # do_reflow = False
        # # soaking_started = 0.0
        # # last_setpoint = 0.0
        # # temp_setpoint = 0.0
        # # temp_soaktime = 0.0
        # # overshoot_prevention = 0
        # # current_overshoot_step = None
        # # heating_top = False
        # # heating_bottom = False
        # # buzzer.jingle()
        # # if soft:
            # # print ('Reflow process finished. Please, open oven door!')
        # # else:
            # # print ('Reflow process has been interrupted. Please, open oven door!')

    # # while True:
        # # now = ticks_ms()
        # # heater_duty[HEATER_NAME_TOP] = heater_top.duty()
        # # heater_duty[HEATER_NAME_BOTTOM] = heater_bottom.duty()
        # # with lock as l:
            # # thermocouples.read_temps()
        # # pcb_temp = thermocouples.temp[pcb_thermocouple][0]
        # # if pcb_temp > FAN_HIGH_DUTY_TEMP:
            # # fan.duty(FAN_HIGH_DUTY)
        # # elif pcb_temp > FAN_LOW_DUTY_TEMP:
            # # fan.duty(FAN_LOW_DUTY)
        # # else:
            # # fan.duty(0)

        # # if do_reflow:
            # # try:
                # # if temp_setpoint == 0:
                    # # if last_setpoint > 0:
                        # # # Setpoint of 0 at end of reflow cycle -> Shut off
                        # # _shutoff(soft = True)
                    # # else:
                        # # last_setpoint = temp_setpoint
                        # # # Try to read first target values from profile
                        # # (temp_setpoint,
                         # # temp_soaktime,
                         # # overshoot_prevention) = reflow_profile_table.popleft()
                        # # print ('Reflow process started...')
                        # # print ('Temperature setpoint:', temp_setpoint, 'Soak time:', temp_soaktime)
                        # # # May produce an IndexError if no more values are in
                        # # # the reflow table, which we'll handle in the
                        # # # 'except' branch

                        # # # Calculate Overshoot Prevention
                        # # overshoot_index = 0
                        # # overshoot_steps = [
                            # # (temp_setpoint - 10 * (overshoot_prevention - i + 1),
                             # # max(HEATER_TOP_MAX_DUTY - 20 * i, 0),
                             # # max(HEATER_BOTTOM_MAX_DUTY - 10 * i, 0))
                             # # for i in range(1, overshoot_prevention + 1)]
                        # # try:
                            # # current_overshoot_step = overshoot_steps[overshoot_index]
                        # # except IndexError:
                            # # current_overshoot_step = None
                # # if temp_setpoint != last_setpoint:
                    # # if (soaking_started > 0.0
                        # # and ticks_diff(now, soaking_started) >= temp_soaktime * 1000):
                            # # print ('Soaking ended...')
                            # # soaking_started = 0.0
                            # # last_setpoint = temp_setpoint
                            # # # Try to read next set of target values from profile
                            # # (temp_setpoint,
                             # # temp_soaktime,
                             # # overshoot_prevention) = reflow_profile_table.popleft()
                            # # print ('Temperature setpoint:', temp_setpoint, 'Soak time:', temp_soaktime)
                            # # # Possible IndexError will be handled later

                            # # # Calculate Overshoot Prevention
                            # # overshoot_index = 0
                            # # overshoot_steps = [
                                # # (temp_setpoint - 10 * (overshoot_prevention - i + 1),
                                 # # max(HEATER_TOP_MAX_DUTY - 20 * i, 0),
                                 # # max(HEATER_BOTTOM_MAX_DUTY - 10 * i, 0))
                                 # # for i in range(1, overshoot_prevention + 1)]

                            # # if overshoot_index < len(overshoot_steps):
                                # # current_overshoot_step = overshoot_steps[overshoot_index]

                # # if temp_setpoint > pcb_temp:
                    # # # Wait one cycle before turning on bottom heater
                    # # # to avoid a surge
                    # # if heating_top and not heating_bottom:
                        # # heater_bottom.duty(HEATER_BOTTOM_MAX_DUTY)
                        # # heating_bottom = True
                    # # if not heating_top:
                        # # heater_top.duty(HEATER_TOP_MAX_DUTY)
                        # # heating_top = True

                    # # # Overshoot prevention
                    # # if (current_overshoot_step is not None and 
                        # # pcb_temp > current_overshoot_step[0]):
                        # # heater_top.duty(current_overshoot_step[1])
                        # # heater_bottom.duty(current_overshoot_step[2])
                        # # overshoot_index += 1

                        # # if overshoot_index < len(overshoot_steps):
                            # # current_overshoot_step = overshoot_steps[overshoot_index]

                # # if heating_top and (temp_setpoint <= pcb_temp):
                    # # if not soaking_started:
                        # # soaking_started = ticks_ms()
                        # # print ('Soaking started...')
                    # # heater_top.duty(0)
                    # # heater_bottom.duty(0)
                    # # heating_top = False
                    # # heating_bottom = False

            # # except IndexError:
                # # # There are no more values in the reflow profile
                # # # SHUT OFF the heaters!
                # # _shutoff(soft = True)

            # # except:
                # # # Something BAD happened.
                # # # SHUT OFF the heaters!
                # # _shutoff()
                # # raise

        # # else:
            # # # In case of a requested shutoff, i.e. by menu command
            # # if heating_top or heating_bottom or soaking_started:
                # # _shutoff()

        # # sleep_ms(500)

def statusDisplayThread(lock):
    """ Display Status, i.e. IP-Address and Temperatures on TFT. """
    global ipaddress, sdcard
    with lock as l:
        tft.show_ipaddress(ipaddress)

    while True:
        with lock as l:
            tft.show_temperatures(thermocouples.temp)
            tft.show_heaters(heat_control.heater_duty)
            if ipaddress != STA().ipaddress:
                ipaddress = STA().ipaddress
                tft.show_ipaddress(ipaddress)
            tft.show_fan(fan.duty())
            tft.show_light(light.pin.value())
            tft.show_sdcard(sdcard.is_mounted())
        sleep(1)

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
_thread.start_new_thread(heat_control.heatReadResponse, ())

# Start Displaying Status (with Locking)
_thread.start_new_thread(statusDisplayThread, (reflowLock, ))

# Start Reading Button Presses (without Locking)
_thread.start_new_thread(buttonThread, ())

# Run Garbage Collector
gc.collect()

##
## Main Menu
##

## Menu Item Switching Callback Functionss (Have to Return True / False)

# Define Menu Items
#  Format:
#   OrderedDict with Menu Item Ids as Keys (Arbitrary Strings)
#    and
#   lists [trigger t, (label0, callback0, cb0 options if trigger == False), (label1, callback1, cb1 options if trigger == True)]
#
# Example Static Menu Item
#  calibrate = [False, ('Calibrate', calibrate, (test = 1)), (None, None, None)]
#
# Example Dynamic Menu Item
#  sdcard = [sd_card_mounted, ('Mount SD Card', mount_sd, None), ('Umount SD Card', umount_sd, None)]

menuitems = [
    [heat_control.isReflowing, 'Start Reflow', heat_control.startReflow, None, 'Stop Reflow', heat_control.cancelReflow, None],
    [light.pin.value, 'Turn on Light', light.pin.on, None, 'Turn off Light', light.pin.off, None],
    [sdcard.is_mounted, 'Mount SD Card', sdcard.mount, None, 'Unmount SD Card', sdcard.umount, None],
    [False, 'Reboot', reset, None, None, None, None],
]

# Set Up Menu
menu = Menu(menuitems, tft, rotary, lock = reflowLock)


##
## Main Code
##

# Initial Menu Display
menu.draw_items()

# Play Jingle
#buzzer.jingle()

# Print Initial Amount of Free Memory
print ('Free Memory:', gc.mem_free())
###
# IDEE:
# Callback-Funktionen / IRQ-Handler fuer Rotary konfigurierbar machen
# a la rotary.button_callback(callback)
###

##
# TODO:
# - SD-Karten Filebrowser
# - File-Headers ili9341 Modul

try:
    """ Handle Menu Input. """
    menu.loop()

finally:
    """ Deinitialize all PWM and SPI Devices.
        !!! Disable Heaters First to Prevent Fires !!!
    """
    heater_bottom.deinit()
    heater_top.deinit()
    fan.deinit()
    buzzer.deinit()
    sdcard.deinit()
