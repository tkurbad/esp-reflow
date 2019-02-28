from micropython import const

from ili9341 import color565
from ili9341.fonts import tt14, tt24
from hwspi.constants import HSPI, VSPI

# Thermocouple Settings
THERMOCOUPLE_BUSID      = HSPI
THERMOCOUPLE_BAUDRATE   = const(1320000)
THERMOCOUPLE_CS1        = const(15)
THERMOCOUPLE_CS2        = const(2)
THERMOCOUPLE_CS3        = const(4)
THERMOCOUPLE_NAME1      = 'tc1'
THERMOCOUPLE_NAME2      = 'tc2'
THERMOCOUPLE_NAME3      = 'tc3'
THERMOCOUPLE_NAME4      = 'int'
THERMOCOUPLE_LABEL      = {
    THERMOCOUPLE_NAME1: 'T1 ',
    THERMOCOUPLE_NAME2: 'T2 ',
    THERMOCOUPLE_NAME3: 'T3 ',
    THERMOCOUPLE_NAME4: 'Int '
}
NUM_THERMOCOUPLES       = const(3)

# SD Card Settings
SDCARD_BUSID            = HSPI
SDCARD_BAUDRATE         = THERMOCOUPLE_BAUDRATE
SDCARD_CS               = const(33)

# Display Hardware Settings
DISPLAY_BUSID           = VSPI
DISPLAY_BAUDRATE        = const(50000000)
DISPLAY_DC_PIN          = const(21)
DISPLAY_CS_PIN          = const(22)

DISPLAY_HEIGHT          = const(320)
DISPLAY_WIDTH           = const(240)

# Display Basic Color / Font Settings
DISPLAY_LABEL_FONT      = tt14
DISPLAY_LABEL_X         = const(10)
DISPLAY_BG_COLOR        = color565(0, 0, 0)
DISPLAY_STATUS_BG_COLOR = color565(200, 200, 200)
DISPLAY_STATUS_FG_COLOR = DISPLAY_BG_COLOR

# Buzzer
BUZZER_PIN              = const(0)
BUZZER_PWM_TIMER        = const(1)
BUZZER_VOLUME           = 30.0
BUZZER_NOTE_CSHARP      = dict()
_CSHARP_BASE            = 17.323914
for octave in range(0, 12):
    BUZZER_NOTE_CSHARP[octave] = const(int(round(_CSHARP_BASE)))
    _CSHARP_BASE        *= 2

# Heaters
HEATER_NAME_TOP         = 'top'
HEATER_NAME_BOTTOM      = 'bottom'
HEATER_LABEL            = {
    HEATER_NAME_TOP: 'Top ',
    HEATER_NAME_BOTTOM: 'Bot '
}
HEATER_BOTTOM_PIN       = const(27)
HEATER_TOP_PIN          = const(26)
HEATER_PWM_FREQ         = const(5)
HEATER_PWM_TIMER        = const(2)
NUM_HEATERS             = const(2)

# Fan
FAN_PIN                 = const(32)
FAN_PWM_FREQ            = const(500)
FAN_PWM_TIMER           = const(3)

# Light
LIGHT_PIN               = const(25)

# Status Bar Display Coordinates
DISPLAY_TOP_BAR_FONT    = tt14
DISPLAY_LOW_BAR_FONT    = tt24
DISPLAY_TOP_BAR_LABEL   = 'Heaters'
DISPLAY_TOP_BAR_LABEL_Y = const(230)
DISPLAY_LOW_BAR_LABEL   = 'Thermocouples'
DISPLAY_LOW_BAR_LABEL_Y = const(250)
DISPLAY_TOP_BAR_Y       = const(0)
DISPLAY_LOW_BAR_Y1      = const(260)
DISPLAY_LOW_BAR_Y2      = const(290)
DISPLAY_TOP_BAR_HEIGHT  = const(19)
DISPLAY_LOW_BAR_HEIGHT  = const(29)
DISPLAY_TOP_BAR_TEXT_X  = const(10)
DISPLAY_TOP_BAR_TEXT_Y  = const(2)
DISPLAY_LOW_BAR_TEXT_X  = {
    THERMOCOUPLE_NAME1: const(10),
    THERMOCOUPLE_NAME2: const(125),
    THERMOCOUPLE_NAME3: const(10),
    THERMOCOUPLE_NAME4: const(125)
}
DISPLAY_LOW_BAR_TEXT_Y  = {
    THERMOCOUPLE_NAME1: const(262),
    THERMOCOUPLE_NAME2: const(262),
    THERMOCOUPLE_NAME3: const(292),
    THERMOCOUPLE_NAME4: const(292)
}

# Heater Bar Display Coordinates
DISPLAY_HEATER_FONT     = tt24
DISPLAY_HEATER_BG_COLOR = DISPLAY_BG_COLOR
DISPLAY_HEATER_FG_COLOR = color565(220, 220, 220)
DISPLAY_HEATER_DELIM_Y  = const(230)
DISPLAY_HEATER_TEXT_X   = {
    HEATER_NAME_TOP: const(10),
    HEATER_NAME_BOTTOM: const(125)
}
DISPLAY_HEATER_TEXT_Y   = const(232)

# Menu Display Settings
MENU_FONT               = tt14
MENU_START_X            = const(5)
MENU_START_Y            = const(25)
MENU_WIDTH              = const(230)
MENU_HEIGHT             = const(180)
MENU_BG_COLOR           = color565(0, 0, 20)
MENU_ACTIVE_BG_COLOR    = color565(0, 236, 234)
MENU_ACTIVE_ITEM_COLOR  = color565(255, 240, 0)
MENU_INACTIVE_BG_COLOR  = color565(0, 0, 20)
MENU_INACTIVE_ITEM_COLOR = color565(255, 240, 0)
