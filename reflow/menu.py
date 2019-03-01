import gc

import config

class Menu:
    active = 0
    last_active = 0

    def __init__(self, menuitems, display, rotary, lock = None):
        """ Initialize Menu Area.

            Parameters:

                menuitems           - ???
                display             - A display.basic.Display Object
                rotary              - A reflow.device.Rotary Object
        """
        self.menuitems = menuitems
        self.num_items = len(menuitems)
        self.display = display
        self.rotary = rotary
        self.lock = lock
        self.clear()
        gc.collect()

    def _clear(self):
        self.display.fill_rectangle(config.MENU_START_X,
                                    config.MENU_START_Y,
                                    config.MENU_WIDTH,
                                    config.MENU_HEIGHT,
                                    color = config.MENU_BG_COLOR)

    def clear(self):
        if self.lock is None:
            self._clear()
            return
        with self.lock as l:
            self._clear()

    def _draw_item(self, index):
        if index == Menu.active:
            self.display.set_color(config.MENU_ACTIVE_ITEM_COLOR,
                                   config.MENU_ACTIVE_BG_COLOR)
        else:
            self.display.set_color(config.MENU_INACTIVE_ITEM_COLOR,
                                   config.MENU_INACTIVE_BG_COLOR)
        name, callback = self.menuitems[index]
        self.display.set_font(config.MENU_FONT)
        self.display.chars(name,
                           config.MENU_START_X + config.MENU_ITEM_OFFSET,
                           config.MENU_START_Y + config.MENU_ITEM_OFFSET + (index * config.MENU_ITEM_SPACING_Y))

    def draw_item(self, index):
        if self.lock is None:
            self._draw_item(index)
            return
        with self.lock as l:
            self._draw_item(index)

    def draw_items(self):
        for index in range(0, self.num_items):
            self.draw_item(index)
        gc.collect()
