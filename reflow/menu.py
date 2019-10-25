# Menu Classes for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

from gc import collect
from utime import sleep_ms

from config import MENU_HEIGHT, MENU_WIDTH, MENU_START_X, MENU_START_Y
from config import MENU_BG_COLOR, MENU_FONT
from config import MENU_ITEM_OFFSET, MENU_ITEM_SPACING_Y
from config import MENU_ACTIVE_ITEM_COLOR, MENU_ACTIVE_BG_COLOR
from config import MENU_INACTIVE_ITEM_COLOR, MENU_INACTIVE_BG_COLOR
from config import ROTARY_RANGE_BOUNDED


class Menu:
    """ Main Menu Display and Handling Class. """

    active = 0          # Currently Active Menu Item
    last_active = 0     # Last Active Menu Item

    def __init__(self, menuitems, display, rotary, button_up = None,
                 button_down = None, button_left = None,
                 button_right = None, lock = None):
        """ Initialize Menu Area.

            Parameters:
                menuitems           - List of
TODO!!!
                display             - A display.basic.Display Object
                rotary              - A reflow.device.Rotary Object
                button_X            - Tuples of 3 Elements:
                                      (reflow.basedevice.PushButton
                                       Object, Callback Function,
                                       Callback Parameters [or None])
        """
        if type(menuitems) != list:
            raise RuntimeError('parameter menuitems must be of type list')
        self.menuitems = menuitems
        self.num_items = len(menuitems)
        self.display = display
        self.rotary = rotary
        # Set Rotary Encoder to Bounded Mode, with Last Menu Item as Max
        # Value
        self.rotary._range_mode = ROTARY_RANGE_BOUNDED
        self.rotary._max_val = self.num_items - 1 if self.num_items > 0 else 0
        self.lock = lock
        self.font_height = MENU_FONT.height()
        self.clear()
        collect()

    def _clear(self):
        """ Clear Menu Area Using Menu Background Color. """
        self.display.fill_rectangle(MENU_START_X,
                                    MENU_START_Y,
                                    MENU_WIDTH,
                                    MENU_HEIGHT,
                                    MENU_BG_COLOR)

    def clear(self):
        """ Clear Menu Area. Use Locking if Lock Has Been Provided. """
        if self.lock is None:
            self._clear()
            self.rotary.reset()
            return
        with self.lock as l:
            self._clear()
        self.rotary.reset()

    @micropython.native
    def _draw_item(self, index):
        """ Draw a Single Menu Item with Number 'index'. """
        if index == Menu.active:
            # Menu Item Is Currently Active - Set Colors Accordingly and
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
        # Extract the Values from the Menuitem at 'index'
        (use_second,
         title1,
         callback1,
         params1,
         title2,
         callback2,
         params2)   = self.menuitems[index]
        if callable(use_second):
            title = title2 if use_second() else title1
        else:
            title = title2 if use_second else title1
        self.display.set_font(MENU_FONT)
        # Display the Menu Item
        self.display.chars(title,
                           MENU_START_X + MENU_ITEM_OFFSET,
                           MENU_START_Y + MENU_ITEM_OFFSET + (index * MENU_ITEM_SPACING_Y))

    def draw_item(self, index):
        """ Draw a Single Menu Item at 'index'. Use Locking if Lock Has
            Been Provided.
        """
        if self.lock is None:
            self._draw_item(index)
            return
        with self.lock as l:
            self._draw_item(index)

    def draw_items(self):
        """ Draw All Menu Items, Highlighting the Currently Active One.
        """
        for index in range(0, self.num_items):
            self.draw_item(index)
        collect()

    def callback_item(self, index):
        """ Run the Callback Function of Menu Item at 'index'. """
        (use_second,
         title1,
         callback1,
         params1,
         title2,
         callback2,
         params2)   = self.menuitems[index]
        if callable(use_second):
            callback = callback2 if use_second() else callback1
            params = params2 if use_second() else params1
        else:
            callback = callback2 if use_second else callback1
            params = params2 if use_second else params1
        if callback is None:
            return
        if params is None:
            callback()
        else:
            callback(params)
        self.draw_item(index)

    def loop(self):
        """ Main Menu Loop. Checks for Rotary Encoder Updates and
            (De-)Activates Menu Items Accordingly.

            TODO: Executes Callback Function of Menuitem Upon Encoder
                  Push Button Press.
        """
        while True:
            # Read Rotary Encoder
            rotary_index, button_pressed = self.rotary.value()
            if button_pressed:
                self.callback_item(Menu.active)
                sleep_ms(50)
                continue
            if Menu.active != rotary_index:
                # Rotary Encoder Has Been Turned
                # Memorize Last Active Menu Item
                Menu.last_active = Menu.active
                # Set New Active Menu Item
                Menu.active = rotary_index
                if self.lock is not None:
                    with self.lock as l:
                        # Display New Active Menu Item as Active
                        self._draw_item(Menu.active)
                        # Display Last Active Menu Item as Inactive
                        self._draw_item(Menu.last_active)
                else:
                    self._draw_item(Menu.active)
                    self._draw_item(Menu.last_active)
            sleep_ms(40)
