# Heat Control Classes for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect

from ucollections import deque
from utime import sleep, sleep_ms, ticks_diff, ticks_ms

from config import FAN_LOW_DUTY, FAN_HIGH_DUTY, FAN_LOW_DUTY_TEMP, FAN_HIGH_DUTY_TEMP
from config import HEATER_BOTTOM_MAX_DUTY, HEATER_TOP_MAX_DUTY
from config import HEATER_NAME_BOTTOM, HEATER_NAME_TOP
from config import THERMOCOUPLE_NAME3 as PCB_THERMOCOUPLE

from reflow.error import ReflowError
from reflow.profile import ReflowProfile


class HeatControl:
    """ Central Heat Reading and Control Class. """

    _reflow             = False     # Is a Reflow in Progress?
    current_setpoint    = 0         # Current Temperature Setpoint
    current_soaktime    = 0         # Soaktime Once Current Setpoint Reached
    last_setpoint       = 0         # Last Temperature Setpoint
    soaking_started     = 0         # When Did Soaking Start?
    soaking_elapsed     = 0         # How Much Soaktime is Elapsed?

    def __init__(self, lock, thermocouples, heater_top, heater_bottom,
                 fan, reflow_profile, buzzer = None, light = None):
        """ Initialize Central Heat Reading and Control Class. """
        self.lock           = lock
        self.thermocouples  = thermocouples
        self.heater_top     = heater_top
        self.heater_bottom  = heater_bottom
        self.fan            = fan
        self._reflow_profile = reflow_profile   # The Reflow Profile to Be Used
        self.buzzer         = buzzer
        self.light          = light

        self._heater_duty   = {     # Save Heater Duty Settings for Speedup
            HEATER_NAME_TOP: 0.0,
            HEATER_NAME_BOTTOM: 0.0
            }

        self._reset()

    def _reset(self):
        """ Reset All Heat Reading and Control Values to their Startup
            Values.
        """
        HeatControl._reflow             = False
        self.heater_top.duty(0)     # Safety First: Disable Heaters
        self.heater_bottom.duty(0)  #               Manually
        self._reflow_profile_table      = deque((), 0, 1)   # Filled Later
        HeatControl.soaking_started     = 0
        HeatControl.soaking_elapsed     = 0
        HeatControl.last_setpoint       = 0
        HeatControl.current_setpoint    = 0
        HeatControl.current_soaktime    = 0
        self._overshoot_prevention      = 0     # Current Overshoot Prevention
        self._current_overshoot_step    = None  #   Step Settings
        self._overshoot_step_index      = 0
        self._heating_top               = False # Is Top Heater Active?
        self._heating_bottom            = False # Is Bottom Heater Active?

    def _readNextSetpoint(self):
        """ Get the Next Setpoint and Soaktime for the Current Profile.
        """
        try:
            (HeatControl.current_setpoint,
             HeatControl.current_soaktime,
             self._overshoot_prevention) = self._reflow_profile_table.popleft()
        except IndexError:
            # No More Entries in Profile Table. End of Profile -> Shutdown.
            self.shutdown(soft = True)

    def _calculateOvershootPreventionSteps(self):
        """ Calculate Heater Intensities at Different Temperature Levels
            for Overshoot Prevention.

            The Number of Overshoot Prevention Steps for Each
            Temperature Setpoint is Provided with the Profile Definition.
        """
        self._overshoot_step_index = 0
        # For Each Step Substract 10°C from the Setpoint and Reduce
        #   Heater Intensity (=PWM Dutycycle) by 20%.
        overshoot_steps = [
            (HeatControl.current_setpoint - 10 * (self._overshoot_prevention - i + 1),
             max(HEATER_TOP_MAX_DUTY - 20 * i, 0),
             max(HEATER_BOTTOM_MAX_DUTY - 10 * i, 0))
             for i in range(1, self._overshoot_prevention + 1)]
        return overshoot_steps

    def shutdown(self, soft = False, error = None):
        """ Shutdown the Reflow Process.

            In Case 'error' is None:
                If 'soft == True' the Operation Was Successful.
                If 'soft == False' the Operation Was Cancelled by the
                User.
            If 'error' is not None an Error Occured (and Will be Shown
                on the Device's TFT Display).
        """
        # Reset to Startup Values.
        self._reset()
        if error is not None:
            # Error? Set it for Later Display and Return.
            ReflowError.setError(error)
            return

        # Play a Nice Jingle
        if self.buzzer is not None:
            self.buzzer.jingle()
        if soft:
            print ('Reflow process finished. Please, open oven door!')
        else:
            print ('Reflow process has been interrupted. Please, open oven door!')

        # Safety First: Make Sure, Reflowing Stops NOW!
        HeatControl._reflow = False

    def heatReadResponse(self):
        """ Read Heater PWM Duty Settings and Thermocouple Values Every
            200 ms.
            If Heating is Requested by the Class variable
            'HeatControl._reflow', Do a "Bang Bang" Control of the Upper
            and Lower Heaters to Follow the Currently Loaded Reflow Profile.
    
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
            now = ticks_ms()        # Save Current Timestamp
            self._heater_duty[HEATER_NAME_TOP]      = self.heater_top.duty()
            self._heater_duty[HEATER_NAME_BOTTOM]   = self.heater_bottom.duty()

            with self.lock as l:
                # Read Temperatures. The Temperature of the PCB to
                #   Reflow is Measured by the PCB_THERMOCOUPLE as
                #   Provided in 'config.py'.
                self.thermocouples.read_temps()
                pcb_temp = self.thermocouples.temp[
                    PCB_THERMOCOUPLE][0]

            # Turn on Fan for Electronics at Pre-Configured Temperatures
            if pcb_temp > FAN_HIGH_DUTY_TEMP:
                self.fan.duty(FAN_HIGH_DUTY)
            elif pcb_temp > FAN_LOW_DUTY_TEMP:
                self.fan.duty(FAN_LOW_DUTY)
            else:
                self.fan.duty(0)

            # Should Reflowing Commence?
            if HeatControl._reflow:
                try:
                    if HeatControl.current_setpoint == 0:
                        if HeatControl.last_setpoint > 0:
                            # Setpoint of 0 at end of reflow cycle -> Shut off
                            self.shutdown(soft = True)
                        else:
                            print ('Reflow process started...')
                            HeatControl.last_setpoint = HeatControl.current_setpoint
                            # Try to read first target values from profile
                            self._readNextSetpoint()
                            print ('Temperature setpoint:',
                                   HeatControl.current_setpoint,
                                   'Soak time:',
                                   HeatControl.current_soaktime)

                            # Calculate Overshoot Prevention
                            overshoot_steps = self._calculateOvershootPreventionSteps()
                            
                            self._current_overshoot_step = None
                            if self._overshoot_step_index < len(overshoot_steps):
                                self._current_overshoot_step = overshoot_steps[self._overshoot_step_index]

                    if HeatControl.current_setpoint != HeatControl.last_setpoint:
                        # Setpoint Changed
                        if HeatControl.soaking_started > 0:
                            HeatControl.soaking_elapsed = ticks_diff(now, HeatControl.soaking_started)
                            if HeatControl.soaking_elapsed >= HeatControl.current_soaktime * 1000:
                                print ('Soaking ended...')
                                HeatControl.soaking_started = 0
                                HeatControl.soaking_elapsed = 0
                                HeatControl.last_setpoint = HeatControl.current_setpoint
                                # Try to read next set of target values from profile
                                self._readNextSetpoint()
                                print ('Temperature setpoint:',
                                       HeatControl.current_setpoint,
                                       'Soak time:',
                                       HeatControl.current_soaktime)

                                # Calculate Overshoot Prevention
                                overshoot_steps = self._calculateOvershootPreventionSteps()

                                if self._overshoot_step_index < len(overshoot_steps):
                                    self._current_overshoot_step = overshoot_steps[self._overshoot_step_index]

                    if HeatControl.current_setpoint > pcb_temp:
                        # Setpoint is Higher than Temperature of the
                        #   Object to Reflow.

                        #   Wait One Cycle Before Turning on the Bottom
                        #   Heater to Avoid a Surge
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

                            if self._overshoot_step_index < len(overshoot_steps):
                                self._current_overshoot_step = overshoot_steps[self._overshoot_step_index]

                    if self._heating_top and (HeatControl.current_setpoint <= pcb_temp):
                        # Setpoint Reached (or Overshot).
                        if not HeatControl.soaking_started:
                            # Start Soaking.
                            HeatControl.soaking_started = now
                            print ('Soaking started...')
                        # Turn Off Heaters.
                        self.heater_top.duty(0)
                        self.heater_bottom.duty(0)
                        self._heating_top = False
                        self._heating_bottom = False

                except:
                    # Something BAD Happened.
                    # SHUT OFF the Heaters!
                    self.shutdown()
                    raise

            else:
                # In Case of a Requested Shutoff, i.e. Cancellation of
                #   Reflow by Menu Command.
                if self._heating_top or self._heating_bottom or HeatControl.soaking_started:
                    self.shutdown()

            # Garbage Collection
            collect()
            sleep_ms(200)

    def buildReflowProfileTable(self, reflow_profile = None):
        if reflow_profile is None:
            reflow_profile = self.reflow_profile

        if reflow_profile is None:
            self.shutdown(error = 'No Reflow Profile!')
            return

        reflow_profile_table = deque((), len(reflow_profile))

        for (setpoint, soaktime, overshoot_prev) in reflow_profile.entries:
            reflow_profile_table.append((setpoint, soaktime, overshoot_prev))

        self._reflow_profile_table = reflow_profile_table
        return reflow_profile_table

    def startReflow(self):
        self.buildReflowProfileTable()
        if self.reflow_profile is None:
            return
        if self.light is not None:
            self.light.pin.on()
        HeatControl._reflow = True

    def cancelReflow(self):
        self.shutdown()

        # Make sure everything is shut off
        self.heater_top.duty(0)
        self.heater_bottom.duty(0)

    @classmethod
    def isReflowing(cls):
        return cls._reflow

    @property
    def heater_duty(self):
        return self._heater_duty

    @property
    def reflow_profile(self):
        return self._reflow_profile

    @reflow_profile.setter
    def reflow_profile(self, reflow_profile):
        if not HeatControl._reflow:
            self._reflow_profile = reflow_profile
