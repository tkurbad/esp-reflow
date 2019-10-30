# Config File for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from micropython import const

from ili9341 import color565
from ili9341.constants import DEFAULT_BAUDRATE, DEFAULT_CS_PIN, DEFAULT_DC_PIN
from ili9341.constants import DEFAULT_HEIGHT, DEFAULT_WIDTH
from ili9341.fonts import tt14, tt24, verdanab16
from hwspi.constants import HSPI, VSPI

# Thermocouple Settings
THERMOCOUPLE_BUSID      = HSPI              # Hardware SPI Bus Id for Thermocouples
THERMOCOUPLE_BAUDRATE   = const(5000000)    # Baudrate for Thermocouple Reads
THERMOCOUPLE_CS1        = const(15)         # Chip Select Pin Number for 1st Thermocouple
THERMOCOUPLE_CS2        = const(2)          # Chip Select Pin Number for 2nd Thermocouple
THERMOCOUPLE_CS3        = const(4)          # Chip Select Pin Number for 3rd Thermocouple
THERMOCOUPLE_NAME1      = 'tc1'             # Index Name for 1st Thermocouple
THERMOCOUPLE_NAME2      = 'tc2'             # Index Name for 2nd Thermocouple
THERMOCOUPLE_NAME3      = 'tc3'             # Index Name for 3rd Thermocouple
THERMOCOUPLE_NAME4      = 'int'             # Index Name for MAX31855 Internal Temperature Sensor
THERMOCOUPLE_LABEL      = {
    THERMOCOUPLE_NAME1: 'TC1 ',             # Label for 1st Thermocouple
    THERMOCOUPLE_NAME2: 'TC2 ',             # Label for 2nd Thermocouple
    THERMOCOUPLE_NAME3: 'TC3 ',             # Label for 3rd Thermocouple
    THERMOCOUPLE_NAME4: 'Int  '             # Label for MAX31855 Internal Temperature Sensor
}
NUM_THERMOCOUPLES       = const(3)          # Number of Physically Connected Thermocouples

# SD Card Settings
SDCARD_BUSID            = HSPI              # Hardware SPI Bus Id for SD Card
SDCARD_BAUDRATE         = THERMOCOUPLE_BAUDRATE # Baudrate for SD Card Reads / Writes
SDCARD_CS               = const(33)         # Chip Select Pin Number for SD Card

# TFT Display Hardware Settings
DISPLAY_BUSID           = VSPI              # Hardware SPI Bus Id for TFT Display
DISPLAY_BAUDRATE        = DEFAULT_BAUDRATE  # Baudrate for TFT Display Reads / Writes
DISPLAY_DC_PIN          = DEFAULT_DC_PIN    # Data/Command Pin Number for TFT Display
DISPLAY_CS_PIN          = DEFAULT_CS_PIN    # Chip Select Pin Number for TFT Display

DISPLAY_HEIGHT          = DEFAULT_HEIGHT    # Height of TFT Display in Pixels
DISPLAY_WIDTH           = DEFAULT_WIDTH     # Width of TFT Display in Pixels

# Display Basic Color / Font Settings
DISPLAY_BG_COLOR        = color565(0, 0, 0)         # Standard Background Color
#  Top Status Bar (IP Address, SD Card Status, ...)
DISPLAY_TOP_BAR_BG_COLOR = color565(200, 200, 200)  # Top Status Bar Background Color
DISPLAY_TOP_BAR_FG_COLOR = DISPLAY_BG_COLOR         # Top Status Bar Foreground Color
#  Bottom Status Bars (Heater Activity, Thermocouple Readings)
DISPLAY_LOW_BAR_BG_COLOR = DISPLAY_BG_COLOR         # Lower Status Bars Background Color
DISPLAY_LOW_BAR_FG_COLOR = color565(200, 200, 200)  # Lower Status Bars Foreground Color
#  Delimiters Between Bottom Status Bars
DISPLAY_DELIM_COLOR     = color565(200, 200, 200)   # Horizontal Delimiter Line Color
#  Bottom Status Bar Label Settings ('Heater Activity %', 'Thermocouple Celsius', ...)
DISPLAY_LABEL_FG_COLOR  = color565(200, 200, 200)   # Label Foreground Color
DISPLAY_LABEL_BG_COLOR  = color565(0, 0, 0)         # Label Background Color
DISPLAY_LABEL_FONT      = tt14                      # Label Font
DISPLAY_LABEL_X         = const(10)                 # Label Horizontal Start Coordinate

# Buzzer
BUZZER_PIN              = const(0)          # Buzzer Pin Number
BUZZER_PWM_TIMER        = const(2)          # Buzzer PWM Timer Number
BUZZER_VOLUME           = 30.0              # Buzzer PWM Duty Cycle (if On)
BUZZER_NOTE_CSHARP      = dict()            # Initialize Buzzer C# Notes Frequency Dictionary
_CSHARP_BASE            = 17.323914         # C#0 Frequency
for octave in range(0, 12):                 # Store Frequencies for C#0 to C#12 in Dictionary
    BUZZER_NOTE_CSHARP[octave] = const(int(round(_CSHARP_BASE)))
    _CSHARP_BASE        *= 2

# Fan
FAN_PIN                 = const(32)         # Fan Pin Number
FAN_PWM_FREQ            = const(500)        # Fan PWM Frequency
FAN_PWM_TIMER           = const(3)          # Fan PWM Timer Number
FAN_LOW_DUTY            = const(10)         # Low Throttle Duty Cycle for Fan
FAN_HIGH_DUTY           = const(20)         # High Throttle Duty Cycle for Fan
FAN_LOW_DUTY_TEMP       = const(30)         # Temperature that Triggers Low Throttle for Fan
FAN_HIGH_DUTY_TEMP      = const(100)        # Temperature that Triggers High Throttle for Fan

# Heaters
HEATER_NAME_BOTTOM      = 'bottom'          # Bottom Heater Index Name
HEATER_NAME_TOP         = 'top'             # Top Heater Index Name
HEATER_LABEL            = {
    HEATER_NAME_BOTTOM: 'Bot   ',           # Bottom Heater Label
    HEATER_NAME_TOP: 'Top  '                # Top Heater Label
}
HEATER_BOTTOM_PIN       = const(27)         # Bottom Heater Pin Number
HEATER_TOP_PIN          = const(26)         # Top Heater Pin Number
HEATER_BOTTOM_PWM_TIMER = const(0)          # PWM Timer Number for Bottom Heater
HEATER_TOP_PWM_TIMER    = const(1)          # PWM Timer Number for Top Heater
HEATER_BOTTOM_MAX_DUTY  = const(50)         # 'Full Throttle' Duty for Bottom Heater
HEATER_TOP_MAX_DUTY     = const(100)        # 'Full Throttle' Duty for Top Heater
HEATER_PWM_FREQ         = const(2)          # PWM Frequency for All Heaters
NUM_HEATERS             = const(2)          # Number of Physically Connected Heaters

# Light
LIGHT_PIN               = const(25)         # Light Switch Pin Number

# Push Buttons
DOWN_PUSHBUTTON_PIN     = const(34)         # Lowermost Pushbutton (Button #3) Pin Number
LEFT_PUSHBUTTON_PIN     = const(35)         # Leftmost Pushbutton (Button #4) Pin Number
RIGHT_PUSHBUTTON_PIN    = const(36)         # Rightmost Pushbutton Pin (Button #1) Pin Number
UP_PUSHBUTTON_PIN       = const(39)         # Topmost Pushbutton (Button #2) Pin Number

# Rotary Encoder
ROTARY_CLK_PIN          = const(17)         # Rotary Encoder CLK (A) Pin Number
ROTARY_DT_PIN           = const(16)         # Rotary Encoder DT (B) Pin Number
ROTARY_PUSH_PIN         = const(5)          # Rotary Encoder Push Button Pin Number
ROTARY_MIN_VAL          = const(0)          # Default Minimum Value of Encoder when Bounded
ROTARY_MAX_VAL          = const(10)         # Default Maximum Value of Encoder when Bounded
ROTARY_RANGE_UNBOUNDED  = const(1)          # Encoder Value Range is -MAXINT..MAXINT
ROTARY_RANGE_WRAP       = const(2)          # Encoder Value Range is ROTARY_MIN_VAL..ROTARY_MAX_VAL w/ Wraparound
ROTARY_RANGE_BOUNDED    = const(3)          # Encoder Value Range is ROTARY_MIN_VAL..ROTARY_MAX_VAL w/o Wraparound

# TFT Display Status Settings
#  General
DISPLAY_TOP_BAR_FONT    = tt14              # Top Status Bar Font
DISPLAY_LOW_BAR_FONT    = tt24              # Bottom Status Bars Font
#  Top Status Bar
DISPLAY_TOP_BAR_Y       = const(0)          # Top Status Bar Vertical Start Coordinate
DISPLAY_TOP_BAR_HEIGHT  = const(18)         # Top Status Bar Height
DISPLAY_TOP_BAR_TEXT_X  = const(10)         # Top Status Bar Horizontal Text Start Coordinate
DISPLAY_TOP_BAR_TEXT_Y  = const(2)          # Top Status Bar Vertical Text Start Coordinate
DISPLAY_FAN_ICON_X      = const(145)        # Top Status Bar Cooling Fan Icon Horizontal Start Coordinate
DISPLAY_LIGHT_ICON_X    = const(202)        # Top Status Bar Light Indicator Icon Horizontal Start Coordinate
DISPLAY_SD_ICON_X       = const(220)        # Top Status Bar SD Card Icon Horizontal Start Coordinate
#  Heater Status Bar
DISPLAY_HEATER_FONT     = tt24              # Heater Status Bar Font
DISPLAY_HEATER_LABEL    = 'Heater Activity %'       # Heater Status Label
DISPLAY_HEATER_LABEL_Y  = const(210)        # Heater Status Label Vertical Start Coordinate
DISPLAY_HEATER_DELIM_Y  = const(212)        # Heater Status Delimiter Line Vertical Coordinate
DISPLAY_HEATER_TEXT_X   = {                 # Status Text Horizontal Start Coordinates...
    HEATER_NAME_BOTTOM: const(125),         # ... for Bottom Heater
    HEATER_NAME_TOP: const(10)              # ... for Top Heater
}
DISPLAY_HEATER_TEXT_Y   = const(224)        # Heater Status Text Vertical Start Coordinate
DISPLAY_HEATER_BG_COLOR = DISPLAY_BG_COLOR          # Heater Status Bar Background Color
DISPLAY_HEATER_FG_COLOR = color565(220, 220, 220)   # Heater Status Bar Foreground Color
#  Thermocouple Status Bars
DISPLAY_LOW_BAR_LABEL1  = 'Thermocouple '   # Thermocouple Status Label Part 1
DISPLAY_LOW_BAR_LABEL2  = 'C'               # Thermocouple Status Label Part 2
DISPLAY_LOW_BAR_LABEL_Y = const(250)        # Thermocouple Status Label Vertical Start Coordinate
DISPLAY_LOW_BAR_DELIM_Y = const(252)        # Thermocouple Status Delimiter Line Vertical Coordinate
DISPLAY_LOW_BAR_TEXT_X  = {                 # Status Text Horizontal Start Coordinates...
    THERMOCOUPLE_NAME1: const(10),          # ... for 1st Thermocouple Label
    THERMOCOUPLE_NAME2: const(127),         # ... for 2nd Thermocouple Label
    THERMOCOUPLE_NAME3: const(10),          # ... for 3rd Thermocouple Label
    THERMOCOUPLE_NAME4: const(127)          # ... for MAX31855 Internal Sensor Label
}
DISPLAY_LOW_BAR_TEXT_Y  = {                 # Status Text Vertical Start Coordinates...
    THERMOCOUPLE_NAME1: const(265),         # ... for 1st Thermocouple Label
    THERMOCOUPLE_NAME2: const(265),         # ... for 2nd Thermocouple Label
    THERMOCOUPLE_NAME3: const(293),         # ... for 3rd Thermocouple Label
    THERMOCOUPLE_NAME4: const(293)          # ... for MAX31855 Internal Sensor Label
}
DISPLAY_THERMOCOUPLE_BG_COLOR = DISPLAY_BG_COLOR        # Thermocouple Status Background Color
DISPLAY_THERMOCOUPLE_FG_COLOR = color565(220, 220, 220) # Thermocouple Status Foreground Color

# TFT Display Menu Settings
MENU_FONT               = verdanab16        # Menu Font
MENU_START_X            = const(5)          # Menu Area Horizontal Start Coordinate
MENU_START_Y            = const(25)         # Menu Area Vertical Start Coordinate
MENU_HEIGHT             = const(180)        # Menu Area Height in Pixels
MENU_WIDTH              = const(230)        # Menu Area Width in Pixels
MENU_ITEM_OFFSET        = const(5)          # Menu Item Offset from Horiz./Vert. Start of Menu Area
MENU_ITEM_SPACING_Y     = const(24)         # Vertical Spacing Between Menu Items
MENU_BG_COLOR           = color565(0, 0, 240)       # Menu Area Background Color
MENU_ACTIVE_BG_COLOR    = color565(255, 240, 0)     # Active Menu Item Background Color
MENU_ACTIVE_ITEM_COLOR  = color565(0, 0, 240)       # Active Menu Item Text Color
MENU_INACTIVE_BG_COLOR  = color565(0, 0, 240)       # Inactive Menu Item Background Color
MENU_INACTIVE_ITEM_COLOR = color565(255, 240, 0)    # Inactive Menu Item Text Color

# Reflow Profile Handling
DEFAULT_PROFILE_FILE    = '/def_profile.json'   # Filename of Default Reflow Profile Saved to Flash
DEFAULT_PROFILE_EXT     = '.prf'            # Default Filename Extension for Profiles
DEFAULT_SD_MOUNTPATH    = '/sd'             # Default Path the SD Card is Mounted to
