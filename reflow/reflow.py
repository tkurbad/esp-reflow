# Heat Control Classes for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad
# This is the Central Thread that Does All the Thermocouple Readings and
# Heater Control

from ucollections import deque
from utime import sleep, sleep_ms, ticks_diff, ticks_ms

import config

##
## Cache Some Configuration Variables
##
FAN_LOW_DUTY            = config.FAN_LOW_DUTY
FAN_HIGH_DUTY           = config.FAN_HIGH_DUTY
FAN_LOW_DUTY_TEMP       = config.FAN_LOW_DUTY_TEMP
FAN_HIGH_DUTY_TEMP      = config.FAN_HIGH_DUTY_TEMP
HEATER_BOTTOM_MAX_DUTY  = config.HEATER_BOTTOM_MAX_DUTY
HEATER_TOP_MAX_DUTY     = config.HEATER_TOP_MAX_DUTY
HEATER_NAME_BOTTOM      = config.HEATER_NAME_BOTTOM
HEATER_NAME_TOP         = config.HEATER_NAME_TOP
PCB_THERMOCOUPLE        = config.THERMOCOUPLE_NAME3

class HeatControl:
    """ Central Heat Reading and Control Class. """

    def __init__(self, lock, thermocouples, heater_top, heater_bottom,
                 fan, reflow_profile, buzzer = None, light = None):
        """ Initialize Central Heat Reading and Control Class. """
        self.lock           = lock
        self.thermocouples  = thermocouples
        self.heater_top     = heater_top
        self.heater_bottom  = heater_bottom
        self.reflow_profile = reflow_profile
        self.buzzer         = buzzer
        self.light          = light

        self._heater_duty   = {
            HEATER_NAME_TOP: 0.0,
            HEATER_NAME_BOTTOM: 0.0
            }

        self._reset()

    def _reset(self):
        self.heater_top.duty(0)
        self.heater_bottom.duty(0)
        self._reflow_profile_table      = deque((), 5, 1)
        self._reflow                    = False
        self._soaking_started           = 0
        self._last_setpoint             = 0
        self._current_setpoint          = 0
        self._current_soaktime          = 0
        self._overshoot_prevention      = 0
        self._current_overshoot_step    = None
        self._overshoot_step_index      = 0
        self._heating_top               = False
        self._heating_bottom            = False

    def _readNextSetpoint(self):
        try:
            (self._current_setpoint,
             self._current_soaktime,
             self._overshoot_prevention) = self._reflow_profile_table.popleft()
        except IndexError:
            self.shutdown(soft = True)

    def _calculateOvershootPreventionSteps(self):
        self._overshoot_step_index = 0
        overshoot_steps = [
            (self._current_setpoint - 10 * (self._overshoot_prevention - i + 1),
             max(HEATER_TOP_MAX_DUTY - 20 * i, 0),
             max(HEATER_BOTTOM_MAX_DUTY - 10 * i, 0))
             for i in range(1, self._overshoot_prevention + 1)]
        return overshoot_steps

    def shutdown(self, soft = False):
        self.reset()
        if self.buzzer is not None:
            self.buzzer.jingle()
        if soft:
            print ('Reflow process finished. Please, open oven door!')
        else:
            print ('Reflow process has been interrupted. Please, open oven door!')

    def heatReadResponse(self):
        """ Read Heater PWM Duty Settings and Thermocouple Values Every
            500 ms.
            If Heating is Requested by the Boolean 'self._reflow', Do a
            "Bang Bang" Control of the Upper and Lower Heaters to Follow
            the Currently Loaded Reflow Profile.
    
            The Following Rule Applies for Each Temperature Setpoint in the
            Profile:
    
            1) If New Setpoint > Current Setpoint: Heat Up as Fast as
                                                   Possible
            2) If Setpoint is Reached and Soak
                                 Time is not Over: Keep Temperature by
                                                   "Banging" the Heaters Off
                                                   and On again with Reduced
                                                   Power
            3) If New Setpoint == 0 or No New SP:  Turn Heaters Off, Reset
                                                   do_reflow = False, and
                                                   set 'open_door' Alarm
                                                   Flag to True
            4) If New Setpoint > 0, but < Current
                                         Setpoint: Turn Off Heaters, Wait
                                                   for Temperature to Reach
                                                   New Setpoint, Start
                                                   Soaking as in 2)
        """
        while True:
            now = ticks_ms()
            self._heater_duty[HEATER_NAME_TOP]      = self.heater_top.duty()
            self._heater_duty[HEATER_NAME_BOTTOM]   = self.heater_bottom.duty()

            with self.lock as l:
                self.thermocouples.read_temps()
                pcb_temp = self.thermocouples.temp[
                    PCB_THERMOCOUPLE][0]

            if pcb_temp > FAN_HIGH_DUTY_TEMP:
                self.fan.duty(FAN_HIGH_DUTY)
            elif pcb_temp > FAN_LOW_DUTY_TEMP:
                self.fan.duty(FAN_LOW_DUTY)
            else:
                self.fan.duty(0)

            if self._reflow:
                try:
                    if self._current_setpoint == 0:
                        if self._last_setpoint > 0:
                            # Setpoint of 0 at end of reflow cycle -> Shut off
                            self.shutdown(soft = True)
                        else:
                            print ('Reflow process started...')
                            self._last_setpoint = self._current_setpoint
                            # Try to read first target values from profile
                            self._readNextSetpoint()
                            print ('Temperature setpoint:',
                                   self._current_setpoint,
                                   'Soak time:',
                                   self._current_soaktime)

                            # Calculate Overshoot Prevention
                            overshoot_steps = self._calculateOvershootPreventionSteps()
                            
                            self._current_overshoot_step = None
                            if self._overshoot_step_index < len(overshoot_steps):
                                self._current_overshoot_step = overshoot_steps[self._overshoot_step_index]

                        if self._current_setpoint != self._last_setpoint:
                            if (self._soaking_started > 0
                                and ticks_diff(now, self._soaking_started) >= self._current_soaktime * 1000):
                                print ('Soaking ended...')
                                self._soaking_started = 0
                                self._last_setpoint = self._current_setpoint
                                # Try to read next set of target values from profile
                                self._readNextSetpoint()
                                print ('Temperature setpoint:',
                                       self._current_setpoint,
                                       'Soak time:',
                                       self._current_soaktime)

                                # Calculate Overshoot Prevention
                                overshoot_steps = self._calculateOvershootPreventionSteps()

                                if self._overshoot_step_index < len(overshoot_steps):
                                    self._current_overshoot_step = overshoot_steps[self._overshoot_step_index]

                    if temp_setpoint > pcb_temp:
                        # Wait one cycle before turning on bottom heater
                        # to avoid a surge
                        if self._heating_top and not self._heating_bottom:
                            self.heater_bottom.duty(HEATER_BOTTOM_MAX_DUTY)
                            self._heating_bottom = True
                        if not self._heating_top:
                            self.heater_top.duty(HEATER_TOP_MAX_DUTY)
                            self._heating_top = True

                        # Overshoot prevention
                        if (self._current_overshoot_step is not None and
                            pcb_temp > self._current_overshoot_step[0]):
                            self.heater_top.duty(
                                self._current_overshoot_step[1])
                            self.heater_bottom.duty(
                                self._current_overshoot_step[2])
                            self._overshoot_step_index += 1

                            if self._overshoot_index < len(overshoot_steps):
                                self._current_overshoot_step = self._overshoot_steps[overshoot_index]

                    if self._heating_top and (self._current_setpoint <= pcb_temp):
                        if not self._soaking_started:
                            self._soaking_started = ticks_ms()
                            print ('Soaking started...')
                        self.heater_top.duty(0)
                        self.heater_bottom.duty(0)
                        self._heating_top = False
                        self._heating_bottom = False

                except:
                    # Something BAD happened.
                    # SHUT OFF the heaters!
                    self.shutdown()
                    raise

            else:
                # In case of a requested shutoff, i.e. by menu command
                if heating_top or heating_bottom or soaking_started:
                    self.shutdown()

            sleep_ms(500)

    def buildReflowProfileTable(self, reflow_profile = None):
        if reflow_profile is None:
            reflow_profile = self.reflow_profile

        reflow_profile_table = deque((), len(reflow_profile))
        ## TODO: Do something with the reflow_profile to generate the
        #          profile table
        # STATIC Values for now
        reflow_profile_table.append((160, 80, 3))
        reflow_profile_table.append((220, 55, 2))

        self._reflow_profile_table = reflow_profile_table
        return reflow_profile_table

    def startReflow(self):
        self.buildReflowProfileTable()
        if self.light is not None:
            light.pin.on()
        self._reflow = True

    def cancelReflow(self):
        self.reset()
        sleep(1)

        # Make sure everything is shut off
        self.heater_top.duty(0)
        self.heater_bottom.duty(0)

    def isReflowing(self):
        return self._reflow

    @property
    def heater_duty(self):
        return self._heater_duty

    @property
    def reflow_profile(self):
        return self._reflow_profile

    @reflow_profile_table.setter
    def reflow_profile(self, reflow_profile):
        if not self._reflow:
            self._reflow_profile = reflow_profile
