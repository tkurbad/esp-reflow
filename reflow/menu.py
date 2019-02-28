import config

class Menu:
    active = 0
    last_active = 0
    num_items = 0

    def __init__(self, menuitems, display, rotary,
                 x = None, y = None, w = None, h = None,
                 bg_color = None,
                 active_bg_color = None, active_item_color = None, 
                 inactive_bg_color = None, inactive_item_color = None):
        """ Initialize Menu Area.

            Parameters:

                menuitems           - ???
                display             - A display.basic.Display Object
                rotary              - A reflow.device.Rotary Object
                x                   - X Start Coordinate of Menu on
                                      Display in Pixels
                y                   - Y Start Coordinate of Menu on
                                      Display in Pixels
                w                   - Width of Menu on Display in Pixels
                h                   - Height of Menu on Display in
                                      Pixels
                bg_color            - Background Color of Menu Area
                active_bg_color     - Background Color of Active Menu
                                      Item
                active_item_color   - Text Color of Active Menu Item
                inactive_bg_color   - Background Color of Inactive Menu
                                      Items
                inactive_item_color - Text Color of Inactive Menu Items

        """
        self.menuitems = menuitems
        self.num_items = len(menuitems)
        self.rotary = rotary
        self.display = display
        self.x = x
        if x is None:
            self.x = config.MENU_START_X
        self.y = y
        if x is None:
            self.x = config.MENU_START_Y
        self.w = w
        if w is None:
            self.w = config.MENU_WIDTH
        self.h = h
        if h is None:
            self.h = config.MENU_HEIGHT
        self.bg_color = bg_color
        if bg_color is None:
            self.bg_color = config.MENU_BG_COLOR
        self.active_bg_color = active_bg_color
        if active_bg_color is None:
            self.active_bg_color = config.MENU_ACTIVE_BG_COLOR
        self.active_item_color = active_item_color
        if active_item_color is None:
            self.active_item_color = config.MENU_ACTIVE_ITEM_COLOR
        self.inactive_bg_color = inactive_bg_color
        if inactive_bg_color is None:
            self.inactive_bg_color = config.MENU_INACTIVE_BG_COLOR
        self.inactive_item_color = inactive_item_color
        if inactive_item_color is None:
            self.inactive_item_color = config.MENU_INACTIVE_ITEM_COLOR
        self.clear_menu_area()

    def clear_menu_area():
        self.display.fill_rectangle(self.x, self.y, self.w, self.h,
                                    color = self.bg_color)
