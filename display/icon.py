# Define Display Icons for ESP32 Micropython Driven SMD Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

def string_to_icon(ascii_image):
    """ Helper Method to Transform 'ASCII Images' to Bytes. """
    binlists = []
    row_length = 0
    icon_height = 0
    icon_width = 0
    for row in ascii_image.split('\n'):
        row = row.strip()
        if len(row) == 0:
            continue

        if row_length == 0:
            # In the resulting icon, each row will become a column.
            # Thus, the row_length actually will be the height of the
            # icon.
            icon_height = row_length = len(row)
            if len(row) % 8 != 0:
                row_length = 8 * (len(row) // 8 + 1)

        # Append '0' to line to get a multiple of 8
        if len(row) < row_length:
            row.ljust(row_length, '0')

        binlist = [int(row[i:i + 8][::-1], 2) for i in range(0, row_length, 8)]
        binlists.append(binlist)

        # The number of rows will become the width of the icon.
        icon_width = len(binlists)

    # binlists now looks like this:
    # [[upmost_byte_of_first_row, ..., lowermost_byte_of_first_row],
    #  [upmost_byte_of_second_row, ..., lowermost_byte_of_second_row],
    #   ...,
    #  [upmost_byte_of_last_row, ..., lowermost_byte_of_last_row]
    # ]

    # Since first_row is the last column in the resulting bitmap,
    # binlists first has to be reversed:
    binlists.reverse()

    # The following code then unfolds the nested lists to:
    #  [upmost_byte_of_last_row, ..., upmost_byte_of_first_row,
    #   ...,
    #  [lowermost_byte_of_last_row, ..., lowermost_byte_of_first_row]
    binlists_reordered = [y for x in zip(*binlists) for y in x]

    icon_bytes = b''.join([binvalue.to_bytes(1, byteorder = 'big')
                           for binvalue in binlists_reordered])
    return icon_bytes, icon_height, icon_width


class Icon:
    """ Base Class for Static Icons. """

    def __init__(self, bitmask, height, width):
        self._bytes = bitmask
        self._height = height
        self._width = width

    @property
    def data(self):
        return self._bytes

    @property
    def height(self):
        return self._height

    @property
    def width(self):
        return self._width


class AnimatedIcon(Icon):
    """ Base Class for 'Animated' Icons. 

        For an AnimatedIcon Instance, Each Call of the data Property
        Alternates Through the List of Byte Sequences Stored in
        self._bytes.

        All Members of the self._bytes List Have to Have the Same
        Dimensions (Width and Height).
    """

    index = 0          # Active Index of self._bytes Sequence

    def __init__(self, bitmask_list, height, width):
        if type(bitmask_list) != list:
            raise TypeError('First Argument must be a list of bytes sequences.')
        self._bytes = bitmask_list
        self._max_index = len(self._bytes) - 1
        self._height = height
        self._width = width

    @property
    def data(self):
        ret_bytes = self._bytes[self.index]
        self.__class__.index = 0 if self.__class__.index == self._max_index else self.__class__.index + 1
        return ret_bytes


class FanIcon(Icon):
    """ A Cooling Fan Icon.

        __init__ Values Generated by:

        bitmask, height, width = string_to_icon(FanIcon._ascii)
    """
    _ascii = '''
                000011100000
                000111100000
                000111100000
                000011001110
                000011011111
                010001111111
                111111100010
                111110110000
                011100110000
                000001111000
                000001111000
                000001110000
            '''

    def __init__(self):
        bitmask = b'\xe0\xe0\xe0\xce\xdf\x7f\xe2\xb00xxp\x00\x01\x01\x00\x00\x04\x0f\x0f\x07\x00\x00\x00'
        height = 12
        width = 12
        super().__init__(bitmask, height, width)


class AnimatedFanIcon(AnimatedIcon):
    """ An 'Animated' Cooling Fan Icon.

        __init__ Values Generated by:

        bitmask_list = []
        bitmask_list[0], height, width = string_to_icon(AnimatedFanIcon._ascii[0])
        bitmask_list[1], height, width = string_to_icon(AnimatedFanIcon._ascii[1])
    """
    _ascii = ['''
                000011100000
                000111100000
                000111100000
                000011001110
                000011011111
                010001111111
                111111100010
                111110110000
                011100110000
                000001111000
                000001111000
                000001110000
            ''',
            '''
                000000000000
                001100011100
                011110011110
                011100111110
                011100100000
                001111100000
                000001111100
                000001001110
                011111001110
                011110011110
                001110001100
                000000000000
            '''
            ]

    def __init__(self):
        bitmask_list = [
            b'\xe0\xe0\xe0\xce\xdf\x7f\xe2\xb00xxp\x00\x01\x01\x00\x00\x04\x0f\x0f\x07\x00\x00\x00',
            b'\x00\x1c\x9e> \xe0|N\xce\x9e\x8c\x00\x00\x03\x07\x07\x07\x03\x00\x00\x07\x07\x03\x00'
            ]
        height = 12
        width = 12
        super().__init__(bitmask_list, height, width)


class DegreeSymbol(Icon):
    """ A ° Symbol for the tt14 Font that Doesn't Have It.


        __init__ Values Generated by:

        bitmask, height, width = string_to_icon(DegreeSymbol._ascii)
    """
    _ascii = '''
                000000000000
                001100000000
                010010000000
                001100000000
            '''

    def __init__(self):
        bitmask = b'\x0c\x12\x0c\x00\x00\x00\x00\x00'
        height = 12
        width = 4
        super().__init__(bitmask, height, width)


class LightbulbIcon(Icon):
    """ A Lightbulb Icon.

        __init__ Values Generated by:

        bitmask, height, width = string_to_icon(LightbulbIcon._ascii)
    """
    _ascii = '''
                001111000000
                010000100000
                100000011110
                100000001101
                100000001101
                100000011110
                010000100000
                001111000000
            '''

    def __init__(self):
        bitmask = b'<B\x81\x01\x01\x81B<\x00\x00\x07\x0b\x0b\x07\x00\x00'
        height = 12
        width = 8
        super().__init__(bitmask, height, width)


class SDIcon(Icon):
    """ A SD Card Icon.

        __init__ Values Generated by:

        bitmask, height, width = string_to_icon(SDIcon._ascii)
    """
    _ascii = '''
                111101111111
                100010000001
                111000000001
                100000000001
                111000000001
                100000000001
                111000000001
                100000000001
                011100000001
                001111111111
            '''

    def __init__(self):
        bitmask = b'\xfc\x0e\x01\x07\x01\x07\x01\x07\x11\xef\x0f\x08\x08\x08\x08\x08\x08\x08\x08\x0f'
        height = 12
        width = 10
        super().__init__(bitmask, height, width)
