# -*- coding: utf-8-*-
"""This module contains the classes and functions for managing settings and the default settings."""
import sys
import input_dev

"""
#: pre-defined resolutions list
resolutions = (
    (400, 300),
    (640, 480),
    (800, 600),
    (1024, 768)
)
"""

#: default input device bindings for sliced
default_bindings = [
                        [(0,273)], [(0,274)], [(0,276)], [(0,275)], 
                        [(0,276), (0,304)], [(0,275), (0,304)], 
                        [(0, 32)], [(0, 13)], [(0, 119)], [(0, 115)], [(0, 113)], 
                        [(0, 97)], [(0, 114)], [(0, 102)], [(0, 101)], 
                        [(0, 100)], [(0, 116)], [(0, 103)], [(0, 121)], 
                        [(0, 104)], [(0, 27)]
]

_font_file = "/usr/share/fonts/TTF/DejaVuSans.ttf"

#: default settings, used in the absence of **settings file**
default_settings = { "font_filename": _font_file, "menu_font_filename": _font_file, "show_fps":True, "speed":5, "key_bindings":input_dev.KeyBindings(input_dev.InputState(), init_bindings=default_bindings) }

class Settings:
    """This class contains settings used by the game.
    
    Note, that all objects used as values for settings have to have the *__repr__* method defined which should return a string, which evaluated will reconstruct the object. This is required so that settings can be saved to file and loaded form it. Simple types such as int, string, bool and float work that way, so can surely be used."""
    def __init__(self, def_sett=default_settings):
        """*def_sett* - dicitionary with string keys - optional - the default settings to use if those form file can't be loaded. """
        self.filename = "settings.txt"
        self.def_sett = def_sett
        self.reset()
    def set(self, name, value):
        """Sets setting *name* to *value*"""
        self.dat[name] = value
    def get(self, name):
        """Returns value of setting *name*"""
        return self.dat[name]
    def reset(self):
        """Resets settings to defaults"""
        self.dat = self.def_sett
    def save(self):
        """Saves settings to config file (if possible)."""
        print "saving settings..."
        try:
            f = open(self.filename, "w")
            f.write(repr(self.dat))
            f.close()
            return True
        except:
            return False
    def load(self):
        """Loads settings from config file (if possible)."""
        try: 
            f = open(self.filename, "r")
            self.dat = eval(f.read())
            return True
        except:
            return False
    def __str__(self):
        """Return human-readable string representation."""
        return str(self.dat)
        
def speed2dt(speed):
    """Calculate the time between consecutive fall steps using the *speed* parameter; *speed* should be an int between 1 and 9 (inclusively). Returns time between consecutive fall steps in msec."""
    return (10-speed)*400
