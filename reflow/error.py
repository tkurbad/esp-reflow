# Error Message Collection Classes for ESP32 Micropython Driven SMD
# Reflow Oven
#
# MIT license; Copyright (c) 2019 Torsten Kurbad

class ReflowError:
    """ Class to Collect Error Messages. """

    _error_message = None
    _error_originator = None

    @classmethod
    def setError(cls, message = None, originator = None):
        """ Set (Error) Message and - Optionally - Originator, e.g.
            Exception Object.
        """
        cls._error_message = message
        cls._error_originator = originator

    @classmethod
    def getError(cls):
        """ Get the Last (Error) Message and Originator and Clear Both.
        """
        message = cls._error_message
        originator = cls._error_originator
        cls._error_message = None
        cls._error_originator = None
        return(message, originator)
