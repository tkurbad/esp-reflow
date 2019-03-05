# Menu Classes for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

import gc
from time import sleep_ms

import config

class Menu:
    """ Main Menu Display and Handling Class. """

    active = 0          # Currently Active Menu Item
    last_active = 0     # Last Active Menu Item

    def __init__(self, menuitems, display, rotary, lock = None):
        """ Initialize Menu Area.

            Parameters:

                menuitems           - A Tuple of Tuples
                                      ('Menu Item Label', callback, (callback parameters))
                display             - A display.basic.Display Object
                rotary              - A reflow.device.Rotary Object
        """
        self.menuitems = menuitems
        self.num_items = len(menuitems)
        self.display = display
        self.rotary = rotary
        # Set Rotary Encoder to Bounded Mode, with Last Menu Item as Max
        # Value
        self.rotary._range_mode = config.ROTARY_RANGE_BOUNDED
        self.rotary._max_val = self.num_items - 1
        self.lock = lock
        self.font_height = config.MENU_FONT.height()
        self.clear()
        gc.collect()

    def _clear(self):
        """ Clear Menu Area Using Menu Background Color. """
        self.display.fill_rectangle(config.MENU_START_X,
                                    config.MENU_START_Y,
                                    config.MENU_WIDTH,
                                    config.MENU_HEIGHT,
                                    color = config.MENU_BG_COLOR)

    def clear(self):
        """ Clear Menu Area. Use Locking if Lock Has Been Provided. """
        if self.lock is None:
            self._clear()
            self.rotary.reset()
            return
        with self.lock as l:
            self._clear()
        self.rotary.reset()

    def _draw_item(self, index):
        """ Draw a Single Menu Item with Number 'index'. """
        if index == Menu.active:
            # Menu Item Is Currently Active - Set Colors Accordingly and
            # Draw Active Item Background
            self.display.set_color(config.MENU_ACTIVE_ITEM_COLOR,
                                   config.MENU_ACTIVE_BG_COLOR)
            self.display.fill_rectangle(config.MENU_START_X,
                                        config.MENU_START_Y + config.MENU_ITEM_OFFSET + (index * config.MENU_ITEM_SPACING_Y),
                                        config.MENU_WIDTH,
                                        config.MENU_FONT.height(),
                                        color = config.MENU_ACTIVE_BG_COLOR)
        else:
            # Menu Item is Inactive - Set Colors Accordingly and Clear
            # Item Background
            self.display.set_color(config.MENU_INACTIVE_ITEM_COLOR,
                                   config.MENU_INACTIVE_BG_COLOR)
            self.display.fill_rectangle(config.MENU_START_X,
                                        config.MENU_START_Y + config.MENU_ITEM_OFFSET + (index * config.MENU_ITEM_SPACING_Y),
                                        config.MENU_WIDTH,
                                        config.MENU_FONT.height(),
                                        color = config.MENU_INACTIVE_BG_COLOR)
        # Extract the Values from the Menuitem at 'index'
        name, callback, params = self.menuitems[index]
        self.display.set_font(config.MENU_FONT)
        # Display the Menu Item
        self.display.chars(name,
                           config.MENU_START_X + config.MENU_ITEM_OFFSET,
                           config.MENU_START_Y + config.MENU_ITEM_OFFSET + (index * config.MENU_ITEM_SPACING_Y))

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
        gc.collect()

    def loop(self):
        """ Main Menu Loop. Checks for Rotary Encoder Updates and
            (De-)Activates Menu Items Accordingly.

            TODO: Executes Callback Function of Menuitem Upon Encoder
                  Push Button Press.
        """
        while True:
            # Read Rotary Encoder
            rotary_index, button_pressed = self.rotary.value()
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
