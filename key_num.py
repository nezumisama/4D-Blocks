# -*- coding: utf-8-*-
"""This module contains some constants used with key bindings."""
 
KEY_MOV_UP                      = 0 #: Move block up
KEY_MOV_DOWN                    = 1 #: Move block down
KEY_MOV_LEFT                    = 2 #: Move block left
KEY_MOV_RIGHT                   = 3 #: Move block right
KEY_MOV_LEFT_W                  = 4 #: Move block along w axis in positive direction
KEY_MOV_RIGHT_W                 = 5 #: Move block along w axis in negative direction

KEY_FORCE_DROP                  = 6 #: Force block to drop
KEY_TURBO                       = 7 #: Turbo mode (increase speed of fall)

KEY_ROT_XY_CW                   = 8 #: Rotate in XY plane clockwise
KEY_ROT_XY_CCW                  = 9 #: Rotate in XY plane counterclockwise
KEY_ROT_XZ_CW                   = 10 #: Rotate in XZ plane clockwise
KEY_ROT_XZ_CCW                  = 11 #: Rotate in XZ plane counterclockwise
KEY_ROT_XW_CW                   = 12 #: Rotate in XW plane clockwise
KEY_ROT_XW_CCW                  = 13 #: Rotate in XW plane counterclockwise
KEY_ROT_YZ_CW                   = 14 #: Rotate in YZ plane clockwise
KEY_ROT_YZ_CCW                  = 15 #: Rotate in YZ plane counterclockwise
KEY_ROT_YW_CW                   = 16 #: Rotate in YW plane clockwise
KEY_ROT_YW_CCW                  = 17 #: Rotate in YW plane counterclockwise
KEY_ROT_ZW_CW                   = 18 #: Rotate in ZW plane clockwise
KEY_ROT_ZW_CCW                  = 19 #: Rotate in ZW plane counterclockwise

KEY_MENU                        = 20 #: Enter/exit menu

#: List of string labels for the bindings
labels = [ "up", "down", "left", "right", "left (w)", "right (w)", "force drop", "turbo", 
           "rot xy cw", "rot xy ccw", "rot xz cw", "rot xz ccw", "rot xw cw", "rot xw ccw",
           "rot yz cw", "rot yz ccw", "rot yw cw", "rot yw ccw", "rot zw cw", "rot zw ccw" ]
